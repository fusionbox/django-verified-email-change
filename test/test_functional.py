import re
from django.test import TestCase
from django.core import urlresolvers, mail
from django.contrib.auth import get_user_model

User = get_user_model()


def refetch(o):
    return o.__class__.objects.get(pk=o.pk)


class TestFunctional(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='foo', password='foo', email='foo@example.com')
        self.client.login(username='foo', password='foo')

    def _read_confirm_email(self, email):
        urlmatch = re.search(r"https?://[^/]*(/.*confirm/\S*)>", email.body.replace('\n', ''))
        self.assertIsNotNone(urlmatch, "No URL found in sent email")
        return urlmatch.groups()[0]

    def _test_change_start(self):
        request_url = urlresolvers.reverse('verified_email_change:email_change')
        self.client.post(request_url, {
            'email': 'foo2@example.com',
            'password': 'foo',
        })
        assert len(mail.outbox) == 1
        return self._read_confirm_email(mail.outbox[0])

    def test_change_verifies_password(self):
        request_url = urlresolvers.reverse('verified_email_change:email_change')
        r = self.client.post(request_url, {
            'email': 'foo2@example.com',
            'password': 'asdf',
        })
        assert 'Password incorrect' in r.content.decode('utf-8')

    def test_email_change(self):
        confirm_path = self._test_change_start()
        assert refetch(self.user).email == 'foo@example.com'
        r = self.client.post(confirm_path)
        assert r.status_code == 302
        assert refetch(self.user).email == 'foo2@example.com'

    def test_email_change_expires_token(self):
        confirm_path = self._test_change_start()
        self.user.email = 'asdf@example.com'
        self.user.save()

        r = self.client.get(confirm_path)
        assert r.status_code == 404
        r = self.client.post(confirm_path)
        assert r.status_code == 404
        assert refetch(self.user).email == 'asdf@example.com'

    def test_bad_signature(self):
        confirm_path = self._test_change_start()
        confirm_path = confirm_path[:-1] + 'asdf/'
        r = self.client.get(confirm_path)
        assert r.status_code == 404
