from django.dispatch import Signal

email_changed = Signal(providing_args=['user', 'old_email', 'new_email'])
