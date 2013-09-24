from django.test import TestCase
from offers.models import Offer, Provider, Plan, Comment, OfferRequest, OfferUpdate, PlanUpdate
from selenium.webdriver.common.by import By
from model_mommy import mommy
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.core.files import File
from django.conf import settings
from django.contrib.auth.models import User
import os
from django.utils import timezone
from datetime import timedelta


class OfferSignalTests(TestCase):
    def setUp(self):
        self.offer = mommy.make(Offer)
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
