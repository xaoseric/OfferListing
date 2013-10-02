from django.test import TestCase
from offers.models import Offer, Plan, Provider
from django.contrib.auth.models import User
from model_mommy import mommy
from django.core.urlresolvers import reverse


class ProviderOnlyAccess(TestCase):
    def _pre_setup(self):
        super(ProviderOnlyAccess, self)._pre_setup()

        self.provider = mommy.make(Provider)

        self.user = User.objects.create_user('user', 'test@example.com', 'pass')
        self.user.user_profile.provider = self.provider
        self.user.user_profile.save()

        self.offer = mommy.make(
            Offer,
            status=Offer.UNPUBLISHED,
            is_request=True,
            is_ready=False,
            provider=self.provider,
            creator=self.user
        )
        self.plan = mommy.make(Plan, offer=self.offer, location__provider=self.provider)

        self.client.login(username='user', password='pass')

    def setUp(self):
        self.url = reverse('offer:admin_requests')

    def test_can_view_page_with_correct_permissions(self):
        """
        Test that a correctly authenticated provider can view the page
        """

        response = self.client.get(self.url, follow=True)
        self.assertEqual(len(response.redirect_chain), 0)  # No redirects
        self.assertEqual(response.status_code, 200)  # Page did not 404