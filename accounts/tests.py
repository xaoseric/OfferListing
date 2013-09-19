from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('some_user', 'test@example.com', 'password')
        self.client.login(username='some_user', password='password')

    def test_logged_in_user_can_logout(self):
        """
        Tests that a logged in user can log out and is redirected to the login page
        """
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][0], 'http://testserver' + reverse('login'))
        self.assertEqual(response.redirect_chain[0][1], 302)

    def test_logged_out_user_can_logout(self):
        """
        Test that a logged out user can still view the logout page and will be redirected to the login form
        """
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][0], 'http://testserver' + reverse('login'))
        self.assertEqual(response.redirect_chain[0][1], 302)
