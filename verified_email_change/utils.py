from django.core import signing

import ogmios

from . import EMAIL_CHANGE_SALT


def initiate_email_change(user, new_email):
    signed_data = {
        'old_email': user.email,
        'email': new_email,
        'pk': user.pk
    }
    ogmios.send_email('verified_email_change/change_email_confirmation_email.html', {
        'user': user,
        'new_email': new_email,
        'signed_data': signing.dumps(signed_data, salt=EMAIL_CHANGE_SALT, compress=True)
    })
