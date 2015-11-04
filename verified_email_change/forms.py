from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class ChangeEmailForm(forms.ModelForm):
    class Meta:
        fields = ('email', )
        model = User

    def clean_email(self):
        email = self.cleaned_data.get('email')
        assert self.instance is not None
        if email == self.instance.email:
            raise forms.ValidationError(
                _("That is already your email address, no need to change it.")
            )
        return email


class ChangeEmailCheckPasswordForm(ChangeEmailForm):
    password = forms.CharField(
        label=_("Password"),
        help_text=_("Enter your current password."),
        widget=forms.PasswordInput,
    )

    class Meta:
        fields = ('email', )
        model = User

    def clean_password(self):
        assert self.instance is not None
        if not self.instance.check_password(self.cleaned_data['password']):
            raise forms.ValidationError(_("Password incorrect."))
