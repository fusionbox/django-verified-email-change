from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class ChangeEmailForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, help_text="Enter your current password.")
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email is not None:
            if email == self.user.email:
                raise forms.ValidationError("That is already your email address, no need to change it.")
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("That email address is already taken.")
        return email

    def clean_password(self):
        if not self.user.check_password(self.cleaned_data['password']):
            raise forms.ValidationError("Password incorrect.")
