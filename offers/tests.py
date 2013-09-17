from django.test import TestCase
from offers.models import Offer, Provider, Plan, Comment
from model_mommy import mommy
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User


class OfferMethodTests(TestCase):

    def setUp(self):
        self.offers = mommy.make(Offer, _quantity=10)

    def test_unicode_string(self):
        """
        Test that the string version of the offer is correct
        """
        for offer in self.offers:
            name = "{0} ({1})".format(offer.name, offer.provider.name)
            self.assertEqual(name, offer.__unicode__())

    def test_plan_count(self):
        """
        Test that the plan count method returns the correct number of plans
        """
        for i, offer in enumerate(self.offers):
            mommy.make(Plan, _quantity=i+1, offer=offer)
            self.assertEqual(offer.plan_count(), i+1)

    def test_min_cost(self):
        """
        Test that the minimum cost method gets the true minimum cost
        """

        for i, offer in enumerate(self.offers):
            mommy.make(Plan, _quantity=20, offer=offer, cost=i+100)
            mommy.make(Plan, offer=offer, cost=i)

            self.assertEqual(i, offer.min_cost())

    def test_min_cost_with_other(self):
        """
        Test that the minimum cost method gets the true minimum cost and not that of other offers
        """

        # Generate other plans with cheaper costs
        mommy.make(Plan, _quantity=20, cost=0)

        for i, offer in enumerate(self.offers):
            mommy.make(Plan, _quantity=20, offer=offer, cost=i+100)
            mommy.make(Plan, offer=offer, cost=i)

            self.assertEqual(i, offer.min_cost())

    def test_max_cost(self):
        """
        Test that the maximum cost method gets the true maximum cost
        """

        for i, offer in enumerate(self.offers):
            mommy.make(Plan, _quantity=20, offer=offer, cost=i+100)
            mommy.make(Plan, offer=offer, cost=i+1000)

            self.assertEqual(i+1000, offer.max_cost())

    def test_max_cost_with_other(self):
        """
        Test that the maximum cost method gets the true maximum cost and not that of other offers
        """

        # Generate other plans with more expensive costs
        mommy.make(Plan, _quantity=20, cost=10000)

        for i, offer in enumerate(self.offers):
            mommy.make(Plan, _quantity=20, offer=offer, cost=i+100)
            mommy.make(Plan, offer=offer, cost=i+1000)

            self.assertEqual(i+1000, offer.max_cost())

    def test_get_comments_published(self):
        """
        Test the get comments method only gets published comments relating to the current offer
        """

        # Generate random comments as well
        mommy.make(Comment, _quantity=20)

        for i, offer in enumerate(self.offers):
            i += 1
            comments = mommy.make(Comment, offer=offer, _quantity=i, status=Comment.PUBLISHED)
            self.assertEqual(len(comments), offer.get_comments().count())
            for comment in comments:
                self.assertIn(comment, offer.get_comments())

    def test_get_comments_unpublished(self):
        """
        Test the get comments method only gets published comments relating to the current offer
        """

        # Generate random comments as well
        mommy.make(Comment, _quantity=20)

        for i, offer in enumerate(self.offers):
            i += 1
            comments = mommy.make(Comment, offer=offer, _quantity=i, status=Comment.UNPUBLISHED)
            self.assertEqual(offer.get_comments().count(), 0)

    def test_get_comments_deleted(self):
        """
        Test the get comments method only gets published comments relating to the current offer
        """

        # Generate random comments as well
        mommy.make(Comment, _quantity=20)

        for i, offer in enumerate(self.offers):
            i += 1
            comments = mommy.make(Comment, offer=offer, _quantity=i, status=Comment.DELETED)
            self.assertEqual(offer.get_comments().count(), 0)


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
            response = self.client.get(offer.get_absolute_url())

            self.assertEqual(response.status_code, 200)

    def test_can_not_view_unpublished_offers(self):
        """
        Test that you can not view an offer that is not published
        """
        for offer in self.offers:
            offer.status = offer.UNPUBLISHED
            offer.save()
            response = self.client.get(offer.get_absolute_url())

            self.assertEqual(response.status_code, 404)

    def test_can_not_view_draft_offers(self):
        """
        Test that you can not view an offer that is a draft
        """
        for offer in self.offers:
            offer.status = offer.DRAFT
            offer.save()
            response = self.client.get(offer.get_absolute_url())

            self.assertEqual(response.status_code, 404)


class OfferAuthenticatedViewTests(OfferViewTests):
    def setUp(self):
        self.offers = mommy.make(Offer, _quantity=10)
        self.user = User.objects.create_user(username='user', email='example@example.com', password='password')
        self.client.login(username='user', password='password')

    def test_user_cannot_post_invalid_comment(self):
        """
        Test that the user can not post an invalid comment
        """
        post_data = {
            "comment": '',
        }

        for offer in self.offers:
            # Assert initial values
            self.assertEqual(offer.get_comments().count(), 0)


class ProviderMethodTests(TestCase):
    def setUp(self):
        self.providers = mommy.make(Provider, _quantity=10)

    def test_unicode_string(self):
        """
        Test that the unicode string of the provider is their name
        """
        for provider in self.providers:
            self.assertEqual(provider.name, provider.__unicode__())

    def test_image_url_without_url(self):
        """
        Test that the static image url is provided when there is no provider image
        """
        for provider in self.providers:
            self.assertEqual(provider.get_image_url(), settings.STATIC_URL + 'img/no_logo.png')

    def test_offer_count_with_published(self):
        """
        Test that the number of published offers for a provider is correctly shown
        """
        for i, provider in enumerate(self.providers):
            mommy.make(Offer, _quantity=i+1, provider=provider, status=Offer.PUBLISHED)
            self.assertEqual(provider.offer_count(), i+1)

    def test_offer_count_with_unpublished(self):
        """
        Test that the number of published offers for a provider is correctly shown
        """
        for i, provider in enumerate(self.providers):
            mommy.make(Offer, _quantity=i, provider=provider, status=Offer.UNPUBLISHED)
            self.assertEqual(provider.offer_count(), 0)

    def test_offer_count_with_draft(self):
        """
        Test that the number of published offers for a provider is correctly shown
        """
        for i, provider in enumerate(self.providers):
            mommy.make(Offer, _quantity=i, provider=provider, status=Offer.DRAFT)
            self.assertEqual(provider.offer_count(), 0)

    def test_plan_count_with_published(self):
        """
        Test the correct amount of plans are shown with the plan_count method
        """
        for i, provider in enumerate(self.providers):
            mommy.make(Plan, _quantity=i+1, offer__provider=provider, offer__status=Offer.PUBLISHED)
            self.assertEqual(provider.plan_count(), i+1)

    def test_plan_count_with_unpublished(self):
        """
        Test the correct amount of plans are shown with the plan_count method
        """
        for i, provider in enumerate(self.providers):
            mommy.make(Plan, _quantity=i+1, offer__provider=provider, offer__status=Offer.UNPUBLISHED)
            self.assertEqual(provider.plan_count(), 0)

    def test_plan_count_with_draft(self):
        """
        Test the correct amount of plans are shown with the plan_count method
        """
        for i, provider in enumerate(self.providers):
            mommy.make(Plan, _quantity=i+1, offer__provider=provider, offer__status=Offer.DRAFT)
            self.assertEqual(provider.plan_count(), 0)


class PlanMethodTests(TestCase):
    def setUp(self):
        self.plans = mommy.make(Plan, _quantity=20)

    def test_data_format_from_MB_to_GB(self):
        """
        Test the data_format method converts correct MB values to GB
        """

        for i in range(100):
            value = i*1024
            plan = mommy.make(Plan)
            result = plan.data_format(value, 'megabytes')

            self.assertEqual("{0} GB".format(i), result)

    def test_data_format_from_GB_to_TB(self):
        """
        Test the data_format method converts correct GB values to TB
        """

        for i in range(100):
            value = i*1024
            plan = mommy.make(Plan)
            result = plan.data_format(value, 'gigabytes')

            self.assertEqual("{0} TB".format(i), result)

    def test_data_format_from_MB_to_MB(self):
        """
        Test the data_format method does not convert invalid MB values to GB
        """

        for i in range(100):
            value = (i*1024) + 1
            plan = mommy.make(Plan)
            result = plan.data_format(value, 'megabytes')

            self.assertEqual("{0} MB".format(value), result)

    def test_data_format_from_GB_to_GB(self):
        """
        Test the data_format method does not convert invalid GB values to TB
        """

        for i in range(100):
            value = (i*1024) + 1
            plan = mommy.make(Plan)
            result = plan.data_format(value, 'gigabytes')

            self.assertEqual("{0} GB".format(value), result)

    def test_get_memory(self):
        """
        Test that the get_memory method returns the correct result
        """

        for plan in self.plans:
            self.assertEqual(plan.get_memory(), plan.data_format(plan.memory, 'megabytes'))

    def test_get_bandwidth(self):
        """
        Test that the get_bandwidth method returns the correct result
        """

        for plan in self.plans:
            self.assertEqual(plan.get_bandwidth(), plan.data_format(plan.bandwidth, 'gigabytes'))

    def test_get_hdd(self):
        """
        Test that the get_hdd method returns the correct result
        """

        for plan in self.plans:
            self.assertEqual(plan.get_hdd(), plan.data_format(plan.disk_space, 'gigabytes'))