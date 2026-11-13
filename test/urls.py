from django.urls import include, path

urlpatterns = [
    path('', include('verified_email_change.urls', 'verified_email_change')),
]
