from django.conf.urls import include, url

urlpatterns = [
    url('^', include('verified_email_change.urls', 'verified_email_change')),
]
