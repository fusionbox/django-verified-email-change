from django.views.generic import FormView, UpdateView
from django.db import transaction
from django.contrib import messages
from django.core import signing
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.auth import get_user_model
from django.conf import settings
from django.shortcuts import resolve_url
from django.utils.functional import cached_property

from decoratormixins.auth import LoginRequiredMixin
import ogmios

from .forms import ChangeEmailForm, ChangeEmailCheckPasswordForm
from .signals import email_changed

User = get_user_model()

EMAIL_CHANGE_SALT = 'verified_email_change.views.URL_SIGNING_SALT'


class SuccessUrlMixin(object):
    def get_success_url(self):
        return resolve_url(settings.LOGIN_REDIRECT_URL)


class ChangeEmailView(LoginRequiredMixin, SuccessUrlMixin, FormView):
    form_class = ChangeEmailCheckPasswordForm
    template_name = 'verified_email_change/change_email.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # If we pass self.request.user to the form, the form will update it when calling
        # form.is_valid(). This will mess up the signed_data computation in View.form_valid().
        # This is why we need a copy of self.request.user:
        kwargs['instance'] = User.objects.get(pk=self.request.user.pk)
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        new_email = form.cleaned_data['email']
        signed_data = {
            'old_email': self.request.user.email,
            'email': new_email,
            'pk': self.request.user.pk
        }
        ogmios.send_email('verified_email_change/change_email_confirmation_email.html', {
            'user': self.request.user,
            'form': form,
            'new_email': new_email,
            'signed_data': signing.dumps(signed_data, salt=EMAIL_CHANGE_SALT, compress=True)
        })
        messages.success(self.request, "A confirmation email has been sent to {}.".format(
            new_email
        ))
        return super().form_valid(form)


class ChangeEmailConfirmView(SuccessUrlMixin, UpdateView):
    template_name = 'verified_email_change/change_email_confirm.html'
    form_class = ChangeEmailForm

    def get_form_kwargs(self):
        kwargs = {
            'instance': self.object,
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
            'data': {'email': self.data['email']},
        }
        return kwargs

    @cached_property
    def data(self):
        try:
            return signing.loads(self.kwargs['signed_data'], salt=EMAIL_CHANGE_SALT)
        except signing.BadSignature:
            raise Http404('Bad signature')

    def get_object(self):
        # Raise a 404 if the user already changed its email address
        return get_object_or_404(User, pk=self.data['pk'], email=self.data['old_email'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data'] = self.data
        return context

    def form_valid(self, form):
        email_changed.send(
            sender=self,
            user=self.object,
            new_email=self.data['email'],
            old_email=self.data['old_email'],
        )
        # TODO: what should be done if request.user != object.user?
        messages.success(self.request, "Your email address has been changed to {}.".format(
            self.data['email']
        ))
        return super().form_valid(form)
