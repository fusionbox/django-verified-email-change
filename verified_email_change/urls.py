from django.urls import re_path

from .views import ChangeEmailView, ChangeEmailConfirmView


app_name = 'verified_email_change'

urlpatterns = [
    re_path(r'change/$', ChangeEmailView.as_view(), name='email_change'),
    re_path(r'confirm/(?P<signed_data>.+)/$',
        ChangeEmailConfirmView.as_view(), name='email_change_confirm'),
]
