from django.conf.urls import url

from .views import ChangeEmailView, ChangeEmailConfirmView


app_name = 'verified_email_change'

urlpatterns = [
    url('change/$', ChangeEmailView.as_view(), name='email_change'),
    url('confirm/(?P<signed_data>.+)/$',
        ChangeEmailConfirmView.as_view(), name='email_change_confirm'),
]
