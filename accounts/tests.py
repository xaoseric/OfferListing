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


class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('some_user', 'test@example.com', 'password')
        self.user.first_name = 'Joe'
        self.user.last_name = 'Bill'
        self.user.save()
        self.client.login(username='some_user', password='password')

    def test_can_view_own_profile(self):
        """
        Test that the user can view their own profile when they are logged in
        """
        response = self.client.get(reverse('profile'))

        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Joe')
        self.assertContains(response, 'Bill')
        self.assertContains(response, 'some_user')

    def test_can_not_view_profile_when_logged_out(self):
        """
        Test that the user can not view the profile page when logged out
        """
        self.client.logout()

        response = self.client.get(reverse('profile'), follow=True)

        self.assertEqual(200, response.status_code)

        self.assertEqual(len(response.redirect_chain), 1)
        self.assertTrue(reverse('login') in response.redirect_chain[0][0])
        self.assertEqual(response.redirect_chain[0][1], 302)
