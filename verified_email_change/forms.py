from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class ChangeEmailForm(forms.ModelForm):
    class Meta:
        fields = ('email', )
        model = User

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email is not None:
            assert self.instance is not None
            if email == self.instance.email:
                raise forms.ValidationError("That is already your email address, no need to change it.")
        return email


class ChangeEmailCheckPasswordForm(ChangeEmailForm):
    password = forms.CharField(widget=forms.PasswordInput, help_text="Enter your current password.")

    class Meta:
        fields = ('email', )
        model = User

    def clean_password(self):
        assert self.instance is not None
        if not self.instance.check_password(self.cleaned_data['password']):
            raise forms.ValidationError("Password incorrect.")
