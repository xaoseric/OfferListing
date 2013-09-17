from django.test import TestCase
from offers.models import Offer, Provider, Plan
from model_mommy import mommy
from django.utils.text import slugify


class OfferMethodTests(TestCase):

    def setUp(self):
        self.offers = mommy.make(Offer, _quantity=10)

    def test_slug_is_correct(self):
        for offer in self.offers:
            slug = "{0}-{1}".format(offer.pk, slugify(offer.name))
            self.assertEqual(slug, offer.slug())
