EMAIL_CHANGE_SALT = 'verified_email_change.views.URL_SIGNING_SALT'

default_app_config = 'verified_email_change.apps.VerifiedEmailChangeConfig'

from .utils import initiate_email_change
