from django.test import TestCase
from offers.models import Offer, Provider
from model_mommy import mommy
from django.utils import timezone
from datetime import timedelta
from django.core import mail
from django.contrib.auth.models import User


class OfferSignalTests(TestCase):
    def setUp(self):
        self.provider = mommy.make(Provider)
        self.user = User.objects.create_user('user', 'test@example.com', 'pass')
        self.user.user_profile.provider = self.provider
        self.user.first_name = "Joe"
        self.user.last_name = "Short"
        self.user.user_profile.save()
        self.user.save()

        self.offer = mommy.make(Offer, provider=self.provider, status=Offer.UNPUBLISHED)
        self.old_time = timezone.now() - timedelta(days=30)

    def test_adds_published_date_on_create(self):
        """
        Test that the published date is added on creation
        """
        self.assertIsNotNone(self.offer.published_at)

    def test_published_at_updated_on_published(self):
        """
        Test that the offer published_at changes when the offer goes from unpublished to published
        """
        self.offer.published_at = self.old_time
        self.offer.status = Offer.UNPUBLISHED
        self.offer.save()

        self.offer.status = Offer.PUBLISHED
        self.offer.save()

        offer = Offer.objects.get(pk=self.offer.pk)
        self.assertNotEqual(offer.published_at, self.old_time)

    def test_published_at_not_update_on_save(self):
        """
        Test that the offer published_at is not updated if other offer data is changed
        """
        self.offer.published_at = self.old_time
        # Update some fields
        self.offer.name = "Some new name"
        self.offer.is_active = False
        # Save these changes
        self.offer.save()

        offer = Offer.objects.get(pk=self.offer.pk)
        self.assertEqual(offer.published_at, self.old_time)

    def test_published_at_not_update_on_published_again(self):
        """
        Test that the published_at field will not update if the offer status has not changed
        """

        # Published remains the same
        self.offer.status = Offer.PUBLISHED
        self.offer.save()

        self.offer.published_at = self.old_time
        self.offer.save()

        self.offer.status = Offer.PUBLISHED
        self.offer.save()

        offer = Offer.objects.get(pk=self.offer.pk)
        self.assertEqual(offer.published_at, self.old_time)

        # Unpublished remains the same
        self.offer.status = Offer.UNPUBLISHED
        self.offer.save()

        self.offer.published_at = self.old_time
        self.offer.save()

        self.offer.status = Offer.UNPUBLISHED
        self.offer.save()

        offer = Offer.objects.get(pk=self.offer.pk)
        self.assertEqual(offer.published_at, self.old_time)

    def test_published_at_not_update_from_published_to_unpublished(self):
        """
        Test that the published_at field does not update when the status changes from PUBLISHED to UNPUBLISHED
        """
        self.offer.status = Offer.PUBLISHED
        self.offer.save()

        self.offer.published_at = self.old_time
        self.offer.save()

        self.offer.status = Offer.UNPUBLISHED
        self.offer.save()

        offer = Offer.objects.get(pk=self.offer.pk)
        self.assertEqual(offer.published_at, self.old_time)

    def test_publishing_an_offer_sends_out_emails(self):
        """
        Test that publishing an offer will send an email to the provider managers
        """
        self.offer.status = Offer.PUBLISHED
        self.offer.save()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.user.email)

        self.assertIn(self.user.first_name, mail.outbox[0].body)
        self.assertIn(self.user.last_name, mail.outbox[0].body)
        self.assertIn(self.offer.get_absolute_url(), mail.outbox[0].body)
        self.assertIn(self.offer.name, mail.outbox[0].body)

    def test_unpublishing_an_offer_sends_no_emails(self):
        """
        Test that unpublishing an offer will not send an email
        """
        self.offer.status = Offer.PUBLISHED
        self.offer.save()

        # Empty outbox
        mail.outbox = []

        self.offer.status = Offer.UNPUBLISHED
        self.offer.save()

        self.assertEqual(len(mail.outbox), 0)

    def test_republishing_an_offer_sends_no_emails(self):
        """
        Test that republishing an offer (saving it twice) will not send an email
        """
        self.offer.status = Offer.PUBLISHED
        self.offer.save()

        # Empty outbox
        mail.outbox = []

        self.offer.status = Offer.PUBLISHED
        self.offer.save()

        self.assertEqual(len(mail.outbox), 0)

    def test_publishing_an_offer_request_sends_no_emails(self):
        """
        Test that publishing an an offer which is a request will not send an email
        """
        self.offer.status = Offer.PUBLISHED
        self.offer.is_request = True
        self.offer.save()

        self.assertEqual(len(mail.outbox), 0)
