from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from accounts.models import UserProfile


class UserProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('some_user', 'test@example.com', 'password')
        self.user.first_name = 'Joe'
        self.user.last_name = 'Bill'
        self.user.save()
        self.client.login(username='some_user', password='password')

    def test_user_has_profile_on_creation(self):
        """
        Test that the post_save signal creates a new UserProfile account on creation of a user
        """
        self.assertNotEqual(self.user.user_profile, None)
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(User.objects.count(), 1)

    def test_user_save_does_not_create_new_profile(self):
        """
        Test that saving a user does not create a new profile
        """
        self.assertNotEqual(self.user.user_profile, None)
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(User.objects.count(), 1)

        self.user.first_name = "new name"
        self.user.save()

        self.assertNotEqual(self.user.user_profile, None)
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(User.objects.count(), 1)

    def test_unicode_name(self):
        """
        Test the unicode name of the profile contains the username
        """
        self.assertIn(self.user.username, self.user.user_profile.__unicode__())
