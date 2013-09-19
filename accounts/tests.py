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


class EditAccountViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('some_user', 'test@example.com', 'password')
        self.user.first_name = 'Joe'
        self.user.last_name = 'Bill'
        self.user.save()
        self.client.login(username='some_user', password='password')

    def test_can_view_edit_form(self):
        """
        Test that a user can view their own edit page
        """
        response = self.client.get(reverse('edit_account'))
        self.assertEqual(response.status_code, 200)

    def test_logged_out_user_can_not_view_edit_form(self):
        """
        Test that a logged out user can not view the edit form of a profile.
        """
        self.client.logout()

        response = self.client.get(reverse('edit_account'), follow=True)

        self.assertEqual(200, response.status_code)

        self.assertEqual(len(response.redirect_chain), 1)
        self.assertTrue(reverse('login') in response.redirect_chain[0][0])
        self.assertEqual(response.redirect_chain[0][1], 302)

    def test_form_updates_user_correctly(self):
        """
        Test that posting the form data correctly updates the user
        """
        data = {
            "first_name": "New_name",
            "last_name": "Last_name",
            "email": "test2@example.com",
        }
        response = self.client.post(reverse('edit_account'), data)

        user = User.objects.get(pk=self.user.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.first_name, data["first_name"])
        self.assertEqual(user.last_name, data["last_name"])
        self.assertEqual(user.email, data["email"])

        self.assertContains(response, 'You account has been successfully updated!')

    def test_form_incorrect_does_not_update_user(self):
        """
        Test that posting incorrect form data will not update the user
        """
        data = {
            "first_name": "",  # Empty name
            "last_name": "Last_name",
            "email": "test2@example",  # Invalid email
        }
        response = self.client.post(reverse('edit_account'), data)

        user = User.objects.get(pk=self.user.pk)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(user.first_name, data["first_name"])
        self.assertNotEqual(user.last_name, data["last_name"])
        self.assertNotEqual(user.email, data["email"])

        self.assertEqual(user.first_name, self.user.first_name)
        self.assertEqual(user.last_name, self.user.last_name)
        self.assertEqual(user.email, self.user.email)

        self.assertContains(response, 'The form had errors. Please correct them and submit again.')


class ChangePasswordTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('some_user', 'test@example.com', 'password')
        self.user.first_name = 'Joe'
        self.user.last_name = 'Bill'
        self.user.save()
        self.client.login(username='some_user', password='password')

    def test_can_view_change_password_form(self):
        """
        Test that a user can view their own change password page
        """
        response = self.client.get(reverse('change_password'))
        self.assertEqual(response.status_code, 200)

    def test_logged_out_user_can_not_view_change_password_form(self):
        """
        Test that a logged out user can not view the change password form
        """
        self.client.logout()

        response = self.client.get(reverse('change_password'), follow=True)

        self.assertEqual(200, response.status_code)

        self.assertEqual(len(response.redirect_chain), 1)
        self.assertTrue(reverse('login') in response.redirect_chain[0][0])
        self.assertEqual(response.redirect_chain[0][1], 302)

    def test_can_change_password(self):
        """
        Test that a user can change their password using the password
        """

        data = {
            "new_password1": 'new_password',
            "new_password2": "new_password",
            "old_password": "password",
        }
        response = self.client.post(reverse('change_password'), data)

        user = User.objects.get(pk=self.user.pk)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You password has been changed!")
        self.assertNotEqual(user.password, self.user.password)

    def test_cant_change_password_with_incorrect_old_password(self):
        """
        Test that the user can not change their password if their old password is not correct
        """
        data = {
            "new_password1": 'new_password',
            "new_password2": "new_password",
            "old_password": "wrong_password",
        }
        response = self.client.post(reverse('change_password'), data)

        user = User.objects.get(pk=self.user.pk)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response,
            'form',
            'old_password',
            'Your old password was entered incorrectly. Please enter it again.',
        )
        self.assertEqual(user.password, self.user.password)

    def test_cant_change_password_with_incorrect_matching_passwords(self):
        """
        Test that the user can not change their password if the two new passwords provided did not match
        """
        data = {
            "new_password1": 'new_password',
            "new_password2": "new_password_wrong",
            "old_password": "password",
        }
        response = self.client.post(reverse('change_password'), data)

        user = User.objects.get(pk=self.user.pk)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response,
            'form',
            'new_password2',
            'The two password fields didn\'t match.',
        )
        self.assertEqual(user.password, self.user.password)


class DeactivateAccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('some_user', 'test@example.com', 'password')
        self.user.first_name = 'Joe'
        self.user.last_name = 'Bill'
        self.user.save()
        self.client.login(username='some_user', password='password')

    def test_can_view_deactivate_account_form(self):
        """
        Test that a user can view their own deactivate account page
        """
        response = self.client.get(reverse('deactivate_account'))
        self.assertEqual(response.status_code, 200)

    def test_logged_out_user_can_not_view_deactivate_account_form(self):
        """
        Test that a logged out user can not view the deactivate account page
        """
        self.client.logout()

        response = self.client.get(reverse('deactivate_account'), follow=True)

        self.assertEqual(200, response.status_code)

        self.assertEqual(len(response.redirect_chain), 1)
        self.assertTrue(reverse('login') in response.redirect_chain[0][0])
        self.assertEqual(response.redirect_chain[0][1], 302)