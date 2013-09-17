from django.test import TestCase
from offers.models import Offer, Provider, Plan
from model_mommy import mommy
from django.utils.text import slugify
from django.core.urlresolvers import reverse


class OfferMethodTests(TestCase):

    def setUp(self):
        self.offers = mommy.make(Offer, _quantity=10)

    def test_slug_is_correct(self):
        """
        Test that the slug returns the correct string
        """
        for offer in self.offers:
            slug = "{0}-{1}".format(offer.pk, slugify(offer.name))
            self.assertEqual(slug, offer.slug())

    def test_unicode_string(self):
        """
        Test that the string version of the offer is correct
        """
        for offer in self.offers:
            name = "{0} ({1})".format(offer.name, offer.provider.name)
            self.assertEqual(name, offer.__unicode__())


class OfferViewTests(TestCase):
    def setUp(self):
        self.offers = mommy.make(Offer, _quantity=10)

    def test_can_view_published_offers(self):
        """
        Test that you can view an offer that is published
        """
        for offer in self.offers:
            offer.status = offer.PUBLISHED
            offer.save()
            response = self.client.get(reverse('offer:view', args=[offer.pk]))

            self.assertEqual(response.status_code, 200)

    def test_can_not_view_unpublished_offers(self):
        """
        Test that you can not view an offer that is not published
        """
        for offer in self.offers:
            offer.status = offer.UNPUBLISHED
            offer.save()
            response = self.client.get(reverse('offer:view', args=[offer.pk]))

            self.assertEqual(response.status_code, 404)

    def test_can_not_view_draft_offers(self):
        """
        Test that you can not view an offer that is a draft
        """
        for offer in self.offers:
            offer.status = offer.DRAFT
            offer.save()
            response = self.client.get(reverse('offer:view', args=[offer.pk]))

            self.assertEqual(response.status_code, 404)


class ProviderMethodTests(TestCase):
    def setUp(self):
        self.providers = mommy.make(Provider, _quantity=10)

    def test_unicode_string(self):
        """
        Test that the unicode string of the provider is their name
        """
        for provider in self.providers:
            self.assertEqual(provider.name, provider.__unicode__())
