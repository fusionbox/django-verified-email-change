from django.views.generic import FormView, DetailView
from django.db import transaction
from django.contrib import messages
from django.core import signing
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.conf import settings
from django.shortcuts import resolve_url

from decoratormixins.auth import LoginRequiredMixin
import ogmios

from .forms import ChangeEmailForm

User = get_user_model()

EMAIL_CHANGE_SALT = 'verified_email_change.views.URL_SIGNING_SALT'


class SuccessUrlMixin(object):
    def get_success_url(self):
        return resolve_url(settings.LOGIN_REDIRECT_URL)


class ChangeEmailView(LoginRequiredMixin, SuccessUrlMixin, FormView):
    form_class = ChangeEmailForm
    template_name = 'verified_email_change/change_email.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
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


class ChangeEmailConfirmView(SuccessUrlMixin, DetailView):
    template_name = 'verified_email_change/change_email_confirm.html'

    def get_object(self):
        try:
            data = signing.loads(self.kwargs['signed_data'], salt=EMAIL_CHANGE_SALT)
        except signing.BadSignature:
            raise Http404('Bad signature')
        else:
            data['user'] = get_object_or_404(User, pk=data['pk'])
            return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email_already_taken'] = self.is_email_already_taken
        context['email_already_changed'] = self.email_already_changed
        return context

    @property
    def is_email_already_taken(self):
        return User.objects.filter(email=self.object['email']).exists()

    @property
    def email_already_changed(self):
        # this ensures that old email change tokens are expired as soon as one
        # of them is used.
        return self.object['user'].email != self.object['old_email']

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.is_email_already_taken or self.email_already_changed:
            return HttpResponseRedirect(self.request.build_absolute_uri())
        # what should be done if request.user != object.user?
        self.object['user'].email = self.object['email']
        self.object['user'].save()
        messages.success(self.request, "Your email address has been changed to {}.".format(
            self.object['email']
        ))
        return HttpResponseRedirect(self.get_success_url())
