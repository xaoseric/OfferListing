from django.test import TestCase
from offers.models import Offer, Provider, Plan, Comment, OfferRequest, OfferUpdate, PlanUpdate, Location
from model_mommy import mommy
from django.core.files import File
from django.conf import settings
from django.contrib.auth.models import User
import os


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

    def test_is_request_with_request_unpublished(self):
        """
        Test the is_request method returns true when there is a request and the offer is unpublished
        """
        offer_request = mommy.make(OfferRequest, offer__status=Offer.UNPUBLISHED)

        self.assertTrue(offer_request.offer.is_request())

    def test_is_request_with_request_published(self):
        """
        Test the is_request method returns false when there is a request and the offer is published
        """
        offer_request = mommy.make(OfferRequest, offer__status=Offer.PUBLISHED)

        self.assertFalse(offer_request.offer.is_request())

    def test_is_request_with_no_request_unpublished(self):
        """
        Test the is_request method returns false when there is no request and the offer is unpublished
        """
        offer = mommy.make(Offer, status=Offer.UNPUBLISHED)

        self.assertFalse(offer.is_request())

    def test_is_request_with_no_request_published(self):
        """
        Test the is_request method returns false when there is no request and the offer is published
        """
        offer = mommy.make(Offer, status=Offer.PUBLISHED)

        self.assertFalse(offer.is_request())


class ProviderMethodTests(TestCase):
    def setUp(self):
        self.provider = mommy.make(Provider)

    def test_unicode_string(self):
        """
        Test that the unicode string of the provider is their name
        """
        self.assertEqual(self.provider.name, self.provider.__unicode__())

    def test_image_url_without_url(self):
        """
        Test that the static image url is provided when there is no provider image
        """
        self.assertEqual(self.provider.get_image_url(), settings.STATIC_URL + 'img/no_logo.png')

    def test_image_with_url(self):
        """
        Test that the real image url is provided when there is a provider image
        """
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data', 'test_image.png')
        self.provider.logo.save(
            image_path,
            File(open(image_path)),
        )
        self.provider.save()
        self.assertNotEqual(self.provider.get_image_url(), '')
        self.assertNotEqual(self.provider.get_image_url(), settings.STATIC_URL + 'img/no_logo.png')
        try:
            os.remove(self.provider.logo.path)
            os.remove(self.provider.logo.path + '.400x400_q85_crop.jpg')
        except OSError:
            pass

    def test_offer_count_with_published_active(self):
        """
        Test that the number of published offers for a provider is correctly shown even if the offer is not active
        """
        mommy.make(Offer, _quantity=20, provider=self.provider, status=Offer.PUBLISHED, is_active=True)
        self.assertEqual(self.provider.offer_count(), 20)

    def test_offer_count_with_unpublished_active(self):
        """
        Test that the number of published offers for a provider is correctly shown even if the offer is not active
        """
        mommy.make(Offer, _quantity=20, provider=self.provider, status=Offer.UNPUBLISHED, is_active=True)
        self.assertEqual(self.provider.offer_count(), 0)

    def test_offer_count_with_published_inactive(self):
        """
        Test that the number of published offers for a provider is correctly shown even if the offer is not active
        """
        mommy.make(Offer, _quantity=20, provider=self.provider, status=Offer.PUBLISHED, is_active=False)
        self.assertEqual(self.provider.offer_count(), 20)

    def test_offer_count_with_unpublished_inactive(self):
        """
        Test that the number of published offers for a provider is correctly shown even if the offer is not active
        """
        mommy.make(Offer, _quantity=20, provider=self.provider, status=Offer.UNPUBLISHED, is_active=False)
        self.assertEqual(self.provider.offer_count(), 0)

    def test_active_offer_count_with_published_active(self):
        """
        Test that the number of published and active offers of a provider are correctly shown
        """
        mommy.make(Offer, _quantity=20, provider=self.provider, status=Offer.PUBLISHED, is_active=True)
        self.assertEqual(self.provider.active_offer_count(), 20)

    def test_active_offer_count_with_unpublished_active(self):
        """
        Test that the number of published and active offers of a provider are correctly shown
        """
        mommy.make(Offer, _quantity=20, provider=self.provider, status=Offer.UNPUBLISHED, is_active=True)
        self.assertEqual(self.provider.active_offer_count(), 0)

    def test_active_offer_count_with_published_inactive(self):
        """
        Test that the number of published and active offers of a provider are correctly shown
        """
        mommy.make(Offer, _quantity=20, provider=self.provider, status=Offer.PUBLISHED, is_active=False)
        self.assertEqual(self.provider.active_offer_count(), 0)

    def test_active_offer_count_with_unpublished_inactive(self):
        """
        Test that the number of published and active offers of a provider are correctly shown
        """
        mommy.make(Offer, _quantity=20, provider=self.provider, status=Offer.UNPUBLISHED, is_active=False)
        self.assertEqual(self.provider.active_offer_count(), 0)

    def test_plan_count_with_active_offer_active_plan_published_offer(self):
        """
        Test that the total plan count is correct when the following conditions are met

        (F is False, T is true)

        If all is T, then the plan is part of the count else it is not

        +--------------+-------------+-----------------+
        | Active Offer | Active Plan | Published Offer |
        +==============+=============+=================+
        |       T      |      T      |        T        |
        +--------------+-------------+-----------------+
        """
        mommy.make(
            Plan,
            _quantity=20,
            offer__provider=self.provider,

            # Variables
            offer__is_active=True,
            is_active=True,
            offer__status=Offer.PUBLISHED,
        )
        self.assertEqual(self.provider.plan_count(), 20)

    def test_plan_count_with_inactive_offer_active_plan_published_offer(self):
        """
        Test that the total plan count is correct when the following conditions are met

        (F is False, T is true)

        If all is T, then the plan is part of the count else it is not

        +--------------+-------------+-----------------+
        | Active Offer | Active Plan | Published Offer |
        +==============+=============+=================+
        |       F      |      T      |        T        |
        +--------------+-------------+-----------------+
        """
        mommy.make(
            Plan,
            _quantity=20,
            offer__provider=self.provider,

            # Variables
            offer__is_active=False,
            is_active=True,
            offer__status=Offer.PUBLISHED,
        )
        self.assertEqual(self.provider.plan_count(), 0)

    def test_plan_count_with_active_offer_inactive_plan_published_offer(self):
        """
        Test that the total plan count is correct when the following conditions are met

        (F is False, T is true)

        If all is T, then the plan is part of the count else it is not

        +--------------+-------------+-----------------+
        | Active Offer | Active Plan | Published Offer |
        +==============+=============+=================+
        |       T      |      F      |        T        |
        +--------------+-------------+-----------------+
        """
        mommy.make(
            Plan,
            _quantity=20,
            offer__provider=self.provider,

            # Variables
            offer__is_active=True,
            is_active=False,
            offer__status=Offer.PUBLISHED,
        )
        self.assertEqual(self.provider.plan_count(), 0)

    def test_plan_count_with_active_offer_active_plan_unpublished_offer(self):
        """
        Test that the total plan count is correct when the following conditions are met

        (F is False, T is true)

        If all is T, then the plan is part of the count else it is not

        +--------------+-------------+-----------------+
        | Active Offer | Active Plan | Published Offer |
        +==============+=============+=================+
        |       T      |      T      |        F        |
        +--------------+-------------+-----------------+
        """
        mommy.make(
            Plan,
            _quantity=20,
            offer__provider=self.provider,

            # Variables
            offer__is_active=True,
            is_active=True,
            offer__status=Offer.UNPUBLISHED,
        )
        self.assertEqual(self.provider.plan_count(), 0)

    def test_plan_count_with_inactive_offer_inactive_plan_unpublished_offer(self):
        """
        Test that the total plan count is correct when the following conditions are met

        (F is False, T is true)

        If all is T, then the plan is part of the count else it is not

        +--------------+-------------+-----------------+
        | Active Offer | Active Plan | Published Offer |
        +==============+=============+=================+
        |       F      |      F      |        F        |
        +--------------+-------------+-----------------+
        """
        mommy.make(
            Plan,
            _quantity=20,
            offer__provider=self.provider,

            # Variables
            offer__is_active=False,
            is_active=False,
            offer__status=Offer.UNPUBLISHED,
        )
        self.assertEqual(self.provider.plan_count(), 0)

    def test_file_path_naming(self):
        """
        Test that the get_file_path() method returns a file with the correct extension
        """
        from offers.models import get_file_path
        filename = 'some_file.png'
        extension = 'png'

        resulting_filename = get_file_path(None, filename)
        self.assertTrue(resulting_filename.endswith(extension))


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


class OfferUpdateMethodTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', email='person@example.com', password='password')
        self.provider = mommy.make(Provider)
        self.user.user_profile.provider = self.provider
        self.user.user_profile.save()

        self.offer = mommy.make(Offer, provider=self.provider, status=Offer.UNPUBLISHED)
        self.plans = mommy.make(Plan, offer=self.offer, _quantity=4)

        self.client.login(username='user', password='password')

    def test_get_update_for_offer_creates_new_offer_update(self):
        """
        Test that using the get_update_for_offer creates a new offer update
        """

        # Assert initial database data
        self.assertEqual(OfferUpdate.objects.count(), 0)
        self.assertEqual(PlanUpdate.objects.count(), 0)

        offer_update = OfferUpdate.objects.get_update_for_offer(self.offer, self.user)

        # Check all values are copied across
        self.assertEqual(offer_update.name, self.offer.name)
        self.assertEqual(offer_update.content, self.offer.content)
        self.assertEqual(offer_update.is_active, self.offer.is_active)
        self.assertEqual(offer_update.provider, self.offer.provider)
        self.assertEqual(offer_update.status, self.offer.status)

        # Check additional fields are correct
        self.assertEqual(offer_update.user, self.user)
        self.assertEqual(offer_update.for_offer, self.offer)

        # Check that all the plans have been copied across
        for i, plan in enumerate(self.offer.plan_set.all()):
            plan_update = offer_update.planupdate_set.all()[i]

            self.assertEqual(plan.virtualization, plan_update.virtualization)
            self.assertEqual(plan.bandwidth, plan_update.bandwidth)
            self.assertEqual(plan.disk_space, plan_update.disk_space)
            self.assertEqual(plan.memory, plan_update.memory)
            self.assertEqual(plan.ipv4_space, plan_update.ipv4_space)
            self.assertEqual(plan.ipv6_space, plan_update.ipv6_space)
            self.assertEqual(plan.billing_time, plan_update.billing_time)
            self.assertEqual(plan.url, plan_update.url)
            self.assertEqual(plan.promo_code, plan_update.promo_code)
            self.assertEqual(plan.cost, plan_update.cost)
            self.assertEqual(plan.is_active, plan_update.is_active)

        # Assert final database data
        self.assertEqual(OfferUpdate.objects.count(), 1)
        self.assertEqual(PlanUpdate.objects.count(), 4)

    def test_get_update_for_offer_gets_existing_offer_update(self):
        """
        Test that the get_update_for_offer method returns the existing offer update for an offer if it already exists
        """
        # Assert initial database data
        self.assertEqual(OfferUpdate.objects.count(), 0)
        self.assertEqual(PlanUpdate.objects.count(), 0)

        # Call the method multiple times
        offer_update1 = OfferUpdate.objects.get_update_for_offer(self.offer, self.user)
        offer_update2 = OfferUpdate.objects.get_update_for_offer(self.offer, self.user)
        offer_update3 = OfferUpdate.objects.get_update_for_offer(self.offer, self.user)
        offer_update4 = OfferUpdate.objects.get_update_for_offer(self.offer, self.user)

        self.assertEqual(offer_update1, offer_update2)
        self.assertEqual(offer_update2, offer_update3)
        self.assertEqual(offer_update3, offer_update4)

        # Assert final database data
        self.assertEqual(OfferUpdate.objects.count(), 1)
        self.assertEqual(PlanUpdate.objects.count(), 4)


class LocationMethodTests(TestCase):
    def setUp(self):
        self.location = mommy.make(Location)

    def test_location_name_with_unicode_name(self):
        """
        Test that the locations still work with unicode country names
        """
        location = mommy.make(Location, country='AX')
        self.assertIn(location.country.name.__unicode__(), location.__unicode__())

    def test_location_name_with_non_unicode_name(self):
        """
        Test that the location name works with a non unicode country name
        """
        location = mommy.make(Location, country='US')
        self.assertIn(location.country.name.__unicode__(), location.__unicode__())