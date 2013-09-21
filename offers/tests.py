from django.test import TestCase
from offers.models import Offer, Provider, Plan, Comment, OfferRequest
from offers.selenium_test import SeleniumTestCase
from selenium.webdriver.common.by import By
from model_mommy import mommy
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.core.files import File
from django.conf import settings
from django.contrib.auth.models import User
import os


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
        from models import get_file_path
        filename = 'some_file.png'
        extension = 'png'

        resulting_filename = get_file_path(None, filename)
        self.assertTrue(resulting_filename.endswith(extension))


class ProviderProfileViewTests(TestCase):
    def setUp(self):
        self.provider = mommy.make(Provider)

    def test_provider_profile_can_be_accessed(self):
        """
        Test that the provider page returns a successful status code
        """
        response = self.client.get(reverse('offer:provider', args=[self.provider.pk]))
        self.assertEqual(response.status_code, 200)

    def test_provider_profile_shows_info(self):
        """
        Test that the provider profile shows the correct info about the provider
        """
        response = self.client.get(reverse('offer:provider', args=[self.provider.pk]))
        self.assertContains(response, self.provider.name)
        self.assertContains(response, self.provider.get_image_url())

    def test_provider_profile_shows_offers(self):
        """
        Test that the provider profile shows the latest offers the provider has
        """
        mommy.make(Offer, _quantity=20, provider=self.provider, status=Offer.PUBLISHED)
        offers = Offer.objects.order_by('-created_at')[0:5]

        response = self.client.get(reverse('offer:provider', args=[self.provider.pk]))

        for offer in offers:
            self.assertContains(response, offer.name)

    def test_provider_profile_shows_offers_paginated(self):
        """
        Test that the provider profile shows the latest offers the provider has using pagination
        """
        mommy.make(Offer, _quantity=20, provider=self.provider, status=Offer.PUBLISHED)

        for page_num in range(4):
            response = self.client.get(reverse('offer:provider_pagination', args=[self.provider.pk, page_num+1]))
            offers = Offer.objects.order_by('-created_at')[page_num*5:(page_num*5) + 5]

            for offer in offers:
                self.assertContains(response, offer.name)

    def test_provider_profile_shows_offers_bad_paginated(self):
        """
        Test that the provider profile shows the latest offers the provider has using pagination even if the page
        is out of the range of pages. The last page should be shown if this happens.
        """
        mommy.make(Offer, _quantity=20, provider=self.provider, status=Offer.PUBLISHED)

        response = self.client.get(reverse('offer:provider_pagination', args=[self.provider.pk, 5]))
        offers = Offer.objects.order_by('-created_at')[15:20]

        for offer in offers:
            self.assertContains(response, offer.name)


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


class OfferAuthenticatedViewTests(OfferViewTests):
    def setUp(self):
        self.offers = mommy.make(Offer, _quantity=10, status=Offer.PUBLISHED)
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
            response = self.client.post(offer.get_absolute_url(), post_data)
            self.assertEqual(offer.get_comments().count(), 0)
            self.assertEqual(response.status_code, 200)

    def test_user_cannot_post_comment_when_logged_out(self):
        """
        Test that the user can not post a comment when they are not logged in
        """
        post_data = {
            "comment": 'Some content',
        }
        self.client.logout()
        for offer in self.offers:
            # Assert initial values
            self.assertEqual(offer.get_comments().count(), 0)
            response = self.client.post(offer.get_absolute_url(), post_data)
            self.assertEqual(offer.get_comments().count(), 0)
            self.assertEqual(response.status_code, 200)

    def test_user_can_post_comment(self):
        """
        Test that the user can post comments on offers
        """
        post_data = {
            "comment": 'Some content',
        }

        for offer in self.offers:
            # Assert initial values
            self.assertEqual(offer.get_comments().count(), 0)
            response = self.client.post(offer.get_absolute_url(), post_data)
            self.assertEqual(offer.get_comments().count(), 1)
            self.assertEqual(response.status_code, 200)

    def test_user_can_post_multiple_comments(self):
        """
        Test that the user can post multiple comments on the same offers
        """
        post_data = {
            "comment": 'Some content',
        }

        for i, offer in enumerate(self.offers):
            # Assert initial values
            self.assertEqual(offer.get_comments().count(), 0)

            for x in range(i):
                response = self.client.post(offer.get_absolute_url(), post_data)
                self.assertEqual(offer.get_comments().count(), x+1)
                self.assertEqual(response.status_code, 200)


class OfferListViewTests(TestCase):
    def setUp(self):
        self.offers = mommy.make(Offer, _quantity=20, status=Offer.PUBLISHED)

    def test_offer_list_view_without_pagination(self):
        """
        Test that the offers page is viewable without any pagination
        """
        response = self.client.get(reverse('home'))
        offers = Offer.objects.order_by('-created_at')[0:5]
        for offer in offers:
            self.assertContains(response, offer.name)

    def test_offer_list_view_with_correct_pagination(self):
        """
        Test that the offers page is viewable with the correct pagination
        """

        # There are 4 pages (with 5 on each)
        for page_num in range(4):
            response = self.client.get(reverse('home_pagination', args=[page_num+1]))
            offers = Offer.objects.order_by('-created_at')[page_num*5:(page_num*5)+5]
            for offer in offers:
                self.assertContains(response, offer.name)

    def test_offer_list_view_with_incorrect_pagination(self):
        """
        Test that the offers page gets the last page if the pagination number is out of the range
        """

        # Get a range of incorrect pages
        for page_number in range(20):
            page_number += 5
            response = self.client.get(reverse('home_pagination', args=[page_number]))
            offers = Offer.objects.order_by('-created_at')[15:20]
            for offer in offers:
                self.assertContains(response, offer.name)


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


class PlanListViewTests(TestCase):
    def setUp(self):
        self.providers = mommy.make(Provider, _quantity=30)

    def test_user_can_view_providers(self):
        """
        Test that a user can view the list of providers
        """
        response = self.client.get(reverse('offer:providers'))

        self.assertEqual(response.status_code, 200)

        for provider in self.providers:
            self.assertContains(response, provider.name)


class ProviderAdminProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', email='person@example.com', password='password')
        self.provider = mommy.make(Provider)
        self.user.user_profile.provider = self.provider
        self.user.user_profile.save()

        self.client.login(username='user', password='password')

    def test_user_can_view_provider_admin_profile(self):
        """
        Test a user which manages a provider can view the provider manage page.
        """
        response = self.client.get(reverse('offer:admin_home'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.provider.name)

    def test_unauthorized_user_can_not_view_provider_admin_profile(self):
        """
        Test a user which can not manage a provider can not access the profile page
        """
        self.user.user_profile.provider = None
        self.user.user_profile.save()
        response = self.client.get(reverse('offer:admin_home'), follow=True)

        self.assertIn(reverse('login'), response.redirect_chain[0][0])
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertEqual(response.status_code, 200)

        self.assertNotContains(response, self.provider.name)


class ProviderAdminNewOfferRequestTests(SeleniumTestCase):
    def setUp(self):
        self.user = User.objects.create_user('user', 'test@example.com', 'password')
        self.provider = mommy.make(Provider)
        self.user.user_profile.provider = self.provider
        self.user.user_profile.save()

        self.login()
        self.open(reverse("offer:admin_request_new"))

    def test_form_has_correct_fields(self):
        """
        Test that the form to submit a request has the correct fields
        """
        # Make sure the main offer info is available
        self.assertTrue(self.is_element_present(By.ID, "id_name"))
        self.assertTrue(self.is_element_present(By.ID, "id_content"))

        # Make sure there are four correct forms
        for i in range(4):
            self.assertTrue(self.is_element_present(By.XPATH, "//div[3]/div[{}]/div".format(i+1)))
            self.assertTrue(self.is_element_present(By.ID, "id_form-{0}-bandwidth".format(i)))
            self.assertTrue(self.is_element_present(By.ID, "id_form-{0}-disk_space".format(i)))
            self.assertTrue(self.is_element_present(By.ID, "id_form-{0}-memory".format(i)))
            self.assertTrue(self.is_element_present(By.ID, "id_form-{0}-virtualization".format(i)))
            self.assertTrue(self.is_element_present(By.ID, "id_form-{0}-ipv4_space".format(i)))
            self.assertTrue(self.is_element_present(By.ID, "id_form-{0}-ipv6_space".format(i)))
            self.assertTrue(self.is_element_present(By.ID, "id_form-{0}-billing_time".format(i)))
            self.assertTrue(self.is_element_present(By.ID, "id_form-{0}-url".format(i)))
            self.assertTrue(self.is_element_present(By.ID, "id_form-{0}-promo_code".format(i)))
            self.assertTrue(self.is_element_present(By.ID, "id_form-{0}-cost".format(i)))

    def test_form_submit_valid_with_no_plans(self):
        """
        Test that a user can submit the form with no plans attached and still have an offer request and an offer
        """

        # Make sure there are no offers and no plans
        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(OfferRequest.objects.count(), 0)
        self.assertEqual(Plan.objects.count(), 0)

        # Submit a new offer
        self.driver.find_element_by_id("id_name").clear()
        self.driver.find_element_by_id("id_name").send_keys("My new offer")
        self.driver.find_element_by_id("id_content").clear()
        self.driver.find_element_by_id("id_content").send_keys("Some content for the new offer")
        self.driver.find_element_by_id("submit-save").click()

        # Make sure the new offer is saved
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 0)  # Make sure there are still no plans

        offer_request = OfferRequest.objects.latest('created_at')

        # Assert automatic values
        self.assertEqual(offer_request.user, self.user)
        self.assertEqual(offer_request.offer.provider, self.provider)
        self.assertEqual(offer_request.offer.status, Offer.UNPUBLISHED)
        self.assertEqual(offer_request.offer.is_active, True)

        # Assert user provided values
        self.assertEqual(offer_request.offer.name, "My new offer")
        self.assertEqual(offer_request.offer.content, "Some content for the new offer")

        # Make sure the user is redirected
        self.assertUrlContains(reverse('offer:admin_request_edit', args=[offer_request.pk]))

    def test_form_submit_valid_with_plans(self):
        """
        Test that a user can submit the form with all valid details (offer and plans) and those are saved correctly
        """

        # Make sure there are no offers and no plans
        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(OfferRequest.objects.count(), 0)
        self.assertEqual(Plan.objects.count(), 0)

        ##  Submit a new offer ##
        # General Details
        self.driver.find_element_by_id("id_name").clear()
        self.driver.find_element_by_id("id_name").send_keys("My new offer")
        self.driver.find_element_by_id("id_content").clear()
        self.driver.find_element_by_id("id_content").send_keys("Some content for the new offer")
        # Form 1
        self.driver.find_element_by_id("id_form-0-bandwidth").clear()
        self.driver.find_element_by_id("id_form-0-bandwidth").send_keys("100")
        self.driver.find_element_by_id("id_form-0-disk_space").clear()
        self.driver.find_element_by_id("id_form-0-disk_space").send_keys("1000")
        self.driver.find_element_by_id("id_form-0-memory").clear()
        self.driver.find_element_by_id("id_form-0-memory").send_keys("1024")
        self.selectOptionBoxById("id_form-0-virtualization", "KVM")
        self.selectOptionBoxById("id_form-0-billing_time", "Monthly")
        self.driver.find_element_by_id("id_form-0-ipv4_space").clear()
        self.driver.find_element_by_id("id_form-0-ipv4_space").send_keys("2")
        self.driver.find_element_by_id("id_form-0-ipv6_space").clear()
        self.driver.find_element_by_id("id_form-0-ipv6_space").send_keys("16")
        self.driver.find_element_by_id("id_form-0-url").clear()
        self.driver.find_element_by_id("id_form-0-url").send_keys("http://example.com/offer/")
        self.driver.find_element_by_id("id_form-0-cost").clear()
        self.driver.find_element_by_id("id_form-0-cost").send_keys("20.00")
        # Form 2
        self.driver.find_element_by_id("id_form-1-bandwidth").clear()
        self.driver.find_element_by_id("id_form-1-bandwidth").send_keys("200")
        self.driver.find_element_by_id("id_form-1-disk_space").clear()
        self.driver.find_element_by_id("id_form-1-disk_space").send_keys("2000")
        self.driver.find_element_by_id("id_form-1-memory").clear()
        self.driver.find_element_by_id("id_form-1-memory").send_keys("2048")
        self.selectOptionBoxById("id_form-1-virtualization", "OpenVZ")
        self.selectOptionBoxById("id_form-1-billing_time", "Yearly")
        self.driver.find_element_by_id("id_form-1-ipv4_space").clear()
        self.driver.find_element_by_id("id_form-1-ipv4_space").send_keys("4")
        self.driver.find_element_by_id("id_form-1-ipv6_space").clear()
        self.driver.find_element_by_id("id_form-1-ipv6_space").send_keys("32")
        self.driver.find_element_by_id("id_form-1-url").clear()
        self.driver.find_element_by_id("id_form-1-url").send_keys("http://example.com/second_offer/segment/")
        self.driver.find_element_by_id("id_form-1-promo_code").clear()
        self.driver.find_element_by_id("id_form-1-promo_code").send_keys("BESTOFFER1")
        self.driver.find_element_by_id("id_form-1-cost").clear()
        self.driver.find_element_by_id("id_form-1-cost").send_keys("40.00")
        # Submit the form
        self.driver.find_element_by_id("submit-save").click()

        # Make sure the new offer is saved
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)

        offer_request = OfferRequest.objects.latest('created_at')
        plan1 = Plan.objects.get(bandwidth=100)
        plan2 = Plan.objects.get(bandwidth=200)

        # Assert automatic values
        self.assertEqual(offer_request.user, self.user)
        self.assertEqual(offer_request.offer.provider, self.provider)
        self.assertEqual(offer_request.offer.status, Offer.UNPUBLISHED)
        self.assertEqual(offer_request.offer.is_active, True)

        self.assertEqual(plan1.is_active, True)
        self.assertEqual(plan2.is_active, True)
        self.assertEqual(plan1.offer, offer_request.offer)
        self.assertEqual(plan2.offer, offer_request.offer)

        # Assert user provided values
        self.assertEqual(offer_request.offer.name, "My new offer")
        self.assertEqual(offer_request.offer.content, "Some content for the new offer")

        self.assertEqual(plan1.bandwidth, 100)
        self.assertEqual(plan1.disk_space, 1000)
        self.assertEqual(plan1.memory, 1024)
        self.assertEqual(plan1.virtualization, Plan.KVM)
        self.assertEqual(plan1.ipv4_space, 2)
        self.assertEqual(plan1.ipv6_space, 16)
        self.assertEqual(plan1.billing_time, Plan.MONTHLY)
        self.assertEqual(plan1.cost, 20.00)
        self.assertEqual(plan1.url, "http://example.com/offer/")
        self.assertEqual(plan1.promo_code, '')

        self.assertEqual(plan2.bandwidth, 200)
        self.assertEqual(plan2.disk_space, 2000)
        self.assertEqual(plan2.memory, 2048)
        self.assertEqual(plan2.virtualization, Plan.OPENVZ)
        self.assertEqual(plan2.ipv4_space, 4)
        self.assertEqual(plan2.ipv6_space, 32)
        self.assertEqual(plan2.billing_time, Plan.YEARLY)
        self.assertEqual(plan2.cost, 40.00)
        self.assertEqual(plan2.url, "http://example.com/second_offer/segment/")
        self.assertEqual(plan2.promo_code, 'BESTOFFER1')

        # Make sure the user is redirected
        self.assertUrlContains(reverse('offer:admin_request_edit', args=[offer_request.pk]))

    def test_form_submit_valid_with_plans_on_different_panels(self):
        """
        Test that a user can submit the form with all valid details (offer and plans) and those are saved correctly even
        if they submit the plans in a seperate order (such as the 1st and 3rd form but leave the second blank)
        """

        # Make sure there are no offers and no plans
        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(OfferRequest.objects.count(), 0)
        self.assertEqual(Plan.objects.count(), 0)

        ##  Submit a new offer ##
        # General Details
        self.driver.find_element_by_id("id_name").clear()
        self.driver.find_element_by_id("id_name").send_keys("My new offer")
        self.driver.find_element_by_id("id_content").clear()
        self.driver.find_element_by_id("id_content").send_keys("Some content for the new offer")
        # Form 1
        self.driver.find_element_by_id("id_form-0-bandwidth").clear()
        self.driver.find_element_by_id("id_form-0-bandwidth").send_keys("100")
        self.driver.find_element_by_id("id_form-0-disk_space").clear()
        self.driver.find_element_by_id("id_form-0-disk_space").send_keys("1000")
        self.driver.find_element_by_id("id_form-0-memory").clear()
        self.driver.find_element_by_id("id_form-0-memory").send_keys("1024")
        self.selectOptionBoxById("id_form-0-virtualization", "KVM")
        self.selectOptionBoxById("id_form-0-billing_time", "Monthly")
        self.driver.find_element_by_id("id_form-0-ipv4_space").clear()
        self.driver.find_element_by_id("id_form-0-ipv4_space").send_keys("2")
        self.driver.find_element_by_id("id_form-0-ipv6_space").clear()
        self.driver.find_element_by_id("id_form-0-ipv6_space").send_keys("16")
        self.driver.find_element_by_id("id_form-0-url").clear()
        self.driver.find_element_by_id("id_form-0-url").send_keys("http://example.com/offer/")
        self.driver.find_element_by_id("id_form-0-cost").clear()
        self.driver.find_element_by_id("id_form-0-cost").send_keys("20.00")
        # Form 2
        self.driver.find_element_by_id("id_form-2-bandwidth").clear()
        self.driver.find_element_by_id("id_form-2-bandwidth").send_keys("200")
        self.driver.find_element_by_id("id_form-2-disk_space").clear()
        self.driver.find_element_by_id("id_form-2-disk_space").send_keys("2000")
        self.driver.find_element_by_id("id_form-2-memory").clear()
        self.driver.find_element_by_id("id_form-2-memory").send_keys("2048")
        self.selectOptionBoxById("id_form-2-virtualization", "OpenVZ")
        self.selectOptionBoxById("id_form-2-billing_time", "Yearly")
        self.driver.find_element_by_id("id_form-2-ipv4_space").clear()
        self.driver.find_element_by_id("id_form-2-ipv4_space").send_keys("4")
        self.driver.find_element_by_id("id_form-2-ipv6_space").clear()
        self.driver.find_element_by_id("id_form-2-ipv6_space").send_keys("32")
        self.driver.find_element_by_id("id_form-2-url").clear()
        self.driver.find_element_by_id("id_form-2-url").send_keys("http://example.com/second_offer/segment/")
        self.driver.find_element_by_id("id_form-2-promo_code").clear()
        self.driver.find_element_by_id("id_form-2-promo_code").send_keys("BESTOFFER1")
        self.driver.find_element_by_id("id_form-2-cost").clear()
        self.driver.find_element_by_id("id_form-2-cost").send_keys("40.00")
        # Submit the form
        self.driver.find_element_by_id("submit-save").click()

        # Make sure the new offer is saved
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)

        offer_request = OfferRequest.objects.latest('created_at')
        plan1 = Plan.objects.get(bandwidth=100)
        plan2 = Plan.objects.get(bandwidth=200)

        # Assert automatic values
        self.assertEqual(offer_request.user, self.user)
        self.assertEqual(offer_request.offer.provider, self.provider)
        self.assertEqual(offer_request.offer.status, Offer.UNPUBLISHED)
        self.assertEqual(offer_request.offer.is_active, True)

        self.assertEqual(plan1.is_active, True)
        self.assertEqual(plan2.is_active, True)
        self.assertEqual(plan1.offer, offer_request.offer)
        self.assertEqual(plan2.offer, offer_request.offer)

        # Assert user provided values
        self.assertEqual(offer_request.offer.name, "My new offer")
        self.assertEqual(offer_request.offer.content, "Some content for the new offer")

        self.assertEqual(plan1.bandwidth, 100)
        self.assertEqual(plan1.disk_space, 1000)
        self.assertEqual(plan1.memory, 1024)
        self.assertEqual(plan1.virtualization, Plan.KVM)
        self.assertEqual(plan1.ipv4_space, 2)
        self.assertEqual(plan1.ipv6_space, 16)
        self.assertEqual(plan1.billing_time, Plan.MONTHLY)
        self.assertEqual(plan1.cost, 20.00)
        self.assertEqual(plan1.url, "http://example.com/offer/")
        self.assertEqual(plan1.promo_code, '')

        self.assertEqual(plan2.bandwidth, 200)
        self.assertEqual(plan2.disk_space, 2000)
        self.assertEqual(plan2.memory, 2048)
        self.assertEqual(plan2.virtualization, Plan.OPENVZ)
        self.assertEqual(plan2.ipv4_space, 4)
        self.assertEqual(plan2.ipv6_space, 32)
        self.assertEqual(plan2.billing_time, Plan.YEARLY)
        self.assertEqual(plan2.cost, 40.00)
        self.assertEqual(plan2.url, "http://example.com/second_offer/segment/")
        self.assertEqual(plan2.promo_code, 'BESTOFFER1')

        # Make sure the user is redirected
        self.assertUrlContains(reverse('offer:admin_request_edit', args=[offer_request.pk]))

    def test_form_submit_with_invalid_plan(self):
        """
        Test that the form does not submit with a missing field in a plan
        """

        # Make sure there are no offers and no plans
        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(OfferRequest.objects.count(), 0)
        self.assertEqual(Plan.objects.count(), 0)

        #  Submit a new offer
        self.driver.find_element_by_id("id_name").clear()
        self.driver.find_element_by_id("id_name").send_keys("Some title")
        self.driver.find_element_by_id("id_content").clear()
        self.driver.find_element_by_id("id_content").send_keys("Some content")
        self.driver.find_element_by_id("id_form-0-bandwidth").clear()
        self.driver.find_element_by_id("id_form-0-bandwidth").send_keys("100")
        self.driver.find_element_by_id("id_form-0-disk_space").clear()
        self.driver.find_element_by_id("id_form-0-disk_space").send_keys("200")
        self.driver.find_element_by_id("id_form-0-memory").clear()
        self.driver.find_element_by_id("id_form-0-memory").send_keys("200")
        self.driver.find_element_by_id("id_form-0-ipv6_space").clear()
        self.driver.find_element_by_id("id_form-0-ipv6_space").send_keys("16")
        self.driver.find_element_by_id("id_form-0-url").clear()
        self.driver.find_element_by_id("id_form-0-url").send_keys("http://example.com")
        self.driver.find_element_by_id("id_form-0-cost").clear()
        self.driver.find_element_by_id("id_form-0-cost").send_keys("20.00")
        self.driver.find_element_by_id("submit-save").click()

        # Make sure an error is displayed
        self.assertEqual("This field is required.", self.driver.find_element_by_css_selector("strong").text)

        # Make sure the url is still on the new request page (won't actually check, __future__ plan)
        self.assertUrlContains(reverse('offer:admin_request_new'))

        # Make sure there are no offers and no plans
        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(OfferRequest.objects.count(), 0)
        self.assertEqual(Plan.objects.count(), 0)

    def test_form_submit_with_invalid_offer(self):
        """
        Test that the form will not submit if the content is missing from the offer field
        """

        # Make sure there are no offers and no plans
        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(OfferRequest.objects.count(), 0)
        self.assertEqual(Plan.objects.count(), 0)

        #  Submit a new offer
        self.driver.find_element_by_id("id_name").clear()
        self.driver.find_element_by_id("id_name").send_keys("Some title")
        self.driver.find_element_by_id("id_form-0-bandwidth").clear()
        self.driver.find_element_by_id("id_form-0-bandwidth").send_keys("100")
        self.driver.find_element_by_id("id_form-0-disk_space").clear()
        self.driver.find_element_by_id("id_form-0-disk_space").send_keys("200")
        self.driver.find_element_by_id("id_form-0-memory").clear()
        self.driver.find_element_by_id("id_form-0-memory").send_keys("200")
        self.driver.find_element_by_id("id_form-0-ipv4_space").clear()
        self.driver.find_element_by_id("id_form-0-ipv4_space").send_keys("1")
        self.driver.find_element_by_id("id_form-0-ipv6_space").clear()
        self.driver.find_element_by_id("id_form-0-ipv6_space").send_keys("16")
        self.driver.find_element_by_id("id_form-0-url").clear()
        self.driver.find_element_by_id("id_form-0-url").send_keys("http://google.com")
        self.driver.find_element_by_id("id_form-0-cost").clear()
        self.driver.find_element_by_id("id_form-0-cost").send_keys("20.00")
        self.driver.find_element_by_id("submit-save").click()

        # Make sure an error is displayed
        self.assertEqual("This field is required.", self.driver.find_element_by_css_selector("strong").text)

        # Make sure the url is still on the new request page (won't actually check, __future__ plan)
        self.assertUrlContains(reverse('offer:admin_request_new'))

        # Make sure there are no offers and no plans
        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(OfferRequest.objects.count(), 0)
        self.assertEqual(Plan.objects.count(), 0)


class ProviderAdminEditOfferRequestTests(SeleniumTestCase):
    def setUp(self):
        self.user = User.objects.create_user('user', 'test@example.com', 'password')
        self.provider = mommy.make(Provider)
        self.user.user_profile.provider = self.provider
        self.user.user_profile.save()

        self.offer = mommy.make(Offer, status=Offer.UNPUBLISHED)
        self.plan1 = mommy.make(Plan, offer=self.offer, cost=200.20, url='http://example.com/first/')
        self.plan2 = mommy.make(Plan, offer=self.offer, cost=3000.82, url='http://example.com/second/')
        self.offer_request = OfferRequest(offer=self.offer, user=self.user)
        self.offer_request.save()

        self.login()
        self.open(reverse("offer:admin_request_edit", args=[self.offer_request.pk]))

    def test_edit_request_form_has_correct_data(self):
        """
        Test that the edit form contains all the correct data to edit a request
        """
        # Assert offer values
        self.assertEqual(self.offer.name, self.driver.find_element_by_id("id_name").get_attribute("value"))
        self.assertEqual(self.offer.content, self.driver.find_element_by_id("id_content").text)

        # Assert plan 1 values
        self.assertEqual(
            str(self.plan1.bandwidth),
            self.driver.find_element_by_id("id_form-0-bandwidth").get_attribute("value")
        )
        self.assertEqual(
            str(self.plan1.disk_space),
            self.driver.find_element_by_id("id_form-0-disk_space").get_attribute("value")
        )
        self.assertEqual(
            str(self.plan1.memory),
            self.driver.find_element_by_id("id_form-0-memory").get_attribute("value")
        )
        self.assertEqual(
            str(self.plan1.ipv4_space),
            self.driver.find_element_by_id("id_form-0-ipv4_space").get_attribute("value")
        )
        self.assertEqual(
            str(self.plan1.ipv6_space),
            self.driver.find_element_by_id("id_form-0-ipv6_space").get_attribute("value")
        )
        self.assertEqual(
            self.plan1.url,
            self.driver.find_element_by_id("id_form-0-url").get_attribute("value")
        )
        self.assertEqual(
            self.plan1.promo_code,
            self.driver.find_element_by_id("id_form-0-promo_code").get_attribute("value")
        )
        self.assertEqual(
            str(self.plan1.cost),
            self.driver.find_element_by_id("id_form-0-cost").get_attribute("value")
        )

        # Assert plan 2 values
        self.assertEqual(
            str(self.plan2.bandwidth),
            self.driver.find_element_by_id("id_form-1-bandwidth").get_attribute("value")
        )
        self.assertEqual(
            str(self.plan2.disk_space),
            self.driver.find_element_by_id("id_form-1-disk_space").get_attribute("value")
        )
        self.assertEqual(
            str(self.plan2.memory),
            self.driver.find_element_by_id("id_form-1-memory").get_attribute("value")
        )
        self.assertEqual(
            str(self.plan2.ipv4_space),
            self.driver.find_element_by_id("id_form-1-ipv4_space").get_attribute("value")
        )
        self.assertEqual(
            str(self.plan2.ipv6_space),
            self.driver.find_element_by_id("id_form-1-ipv6_space").get_attribute("value")
        )
        self.assertEqual(
            self.plan2.url,
            self.driver.find_element_by_id("id_form-1-url").get_attribute("value")
        )
        self.assertEqual(
            self.plan2.promo_code,
            self.driver.find_element_by_id("id_form-1-promo_code").get_attribute("value")
        )
        self.assertEqual(
            str(self.plan2.cost),
            self.driver.find_element_by_id("id_form-1-cost").get_attribute("value")
        )

    def test_can_edit_offer_using_form(self):
        """
        Test that a user can edit a request using the provided form
        """

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)

        # Submit the new values
        self.driver.find_element_by_id("id_name").clear()
        self.driver.find_element_by_id("id_name").send_keys("New title")
        self.driver.find_element_by_id("id_content").clear()
        self.driver.find_element_by_id("id_content").send_keys("New content")
        self.driver.find_element_by_id("submit-save").click()

        # Reload the local instance
        self.offer = Offer.objects.get(pk=self.offer.pk)

        # Make sure the new data is saved to the database
        self.assertEqual(self.offer.name, "New title")
        self.assertEqual(self.offer.content, "New content")

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)

    def test_can_edit_plans_using_form(self):
        """
        Test that a user can edit the plans of an offer request using the provided forms
        """

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)

        # Submit the new values for form 1
        self.driver.find_element_by_id("id_form-0-bandwidth").clear()
        self.driver.find_element_by_id("id_form-0-bandwidth").send_keys("200")
        self.driver.find_element_by_id("id_form-0-disk_space").clear()
        self.driver.find_element_by_id("id_form-0-disk_space").send_keys("100")
        self.driver.find_element_by_id("id_form-0-memory").clear()
        self.driver.find_element_by_id("id_form-0-memory").send_keys("1024")
        self.driver.find_element_by_id("id_form-0-ipv4_space").clear()
        self.driver.find_element_by_id("id_form-0-ipv4_space").send_keys("1")
        self.driver.find_element_by_id("id_form-0-ipv6_space").clear()
        self.driver.find_element_by_id("id_form-0-ipv6_space").send_keys("16")
        self.driver.find_element_by_id("id_form-0-url").clear()
        self.driver.find_element_by_id("id_form-0-url").send_keys("http://example.com/")
        self.driver.find_element_by_id("id_form-0-promo_code").clear()
        self.driver.find_element_by_id("id_form-0-promo_code").send_keys("CHEAP")
        self.driver.find_element_by_id("id_form-0-cost").clear()
        self.driver.find_element_by_id("id_form-0-cost").send_keys("400.00")

        # Submit the new values for form 2
        self.driver.find_element_by_id("id_form-1-disk_space").clear()
        self.driver.find_element_by_id("id_form-1-disk_space").send_keys("300")
        self.driver.find_element_by_id("id_form-1-memory").clear()
        self.driver.find_element_by_id("id_form-1-memory").send_keys("4096")
        self.driver.find_element_by_id("id_form-1-ipv4_space").clear()
        self.driver.find_element_by_id("id_form-1-ipv4_space").send_keys("2")
        self.driver.find_element_by_id("id_form-1-ipv6_space").clear()
        self.driver.find_element_by_id("id_form-1-ipv6_space").send_keys("32")
        self.driver.find_element_by_id("id_form-1-url").clear()
        self.driver.find_element_by_id("id_form-1-url").send_keys("http://example.com/special/")
        self.driver.find_element_by_id("id_form-1-cost").clear()
        self.driver.find_element_by_id("id_form-1-cost").send_keys("800.00")

        # Submit the form
        self.driver.find_element_by_id("submit-save").click()

        # Reload the local instances
        self.plan1 = Plan.objects.get(pk=self.plan1.pk)
        self.plan2 = Plan.objects.get(pk=self.plan2.pk)

        # Assert the data for plan 1 is the same
        self.assertEqual(self.plan1.bandwidth, 200)
        self.assertEqual(self.plan1.disk_space, 100)
        self.assertEqual(self.plan1.memory, 1024)
        self.assertEqual(self.plan1.ipv4_space, 1)
        self.assertEqual(self.plan1.ipv6_space, 16)
        self.assertEqual(self.plan1.url, "http://example.com/")
        self.assertEqual(self.plan1.promo_code, "CHEAP")
        self.assertEqual(self.plan1.cost, 400.00)

        # Assert the data for plan 2 is the same
        self.assertEqual(self.plan2.disk_space, 300)
        self.assertEqual(self.plan2.memory, 4096)
        self.assertEqual(self.plan2.ipv4_space, 2)
        self.assertEqual(self.plan2.ipv6_space, 32)
        self.assertEqual(self.plan2.url, "http://example.com/special/")
        self.assertEqual(self.plan2.promo_code, "")
        self.assertEqual(self.plan2.cost, 800.00)

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)

    def test_saving_does_not_duplicate_data(self):
        """
        Test that saving does not duplicate any database data
        """

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)

        self.driver.find_element_by_id("submit-save").click()

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)

    def test_can_add_new_plans(self):
        """
        Test that the user can add new plans to an offer
        """

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)

        # Send in some new data
        self.driver.find_element_by_id("id_form-2-bandwidth").clear()
        self.driver.find_element_by_id("id_form-2-bandwidth").send_keys("600")
        self.driver.find_element_by_id("id_form-2-disk_space").clear()
        self.driver.find_element_by_id("id_form-2-disk_space").send_keys("200")
        self.driver.find_element_by_id("id_form-2-memory").clear()
        self.driver.find_element_by_id("id_form-2-memory").send_keys("256")
        self.driver.find_element_by_id("id_form-2-ipv4_space").clear()
        self.driver.find_element_by_id("id_form-2-ipv4_space").send_keys("4")
        self.driver.find_element_by_id("id_form-2-ipv6_space").clear()
        self.driver.find_element_by_id("id_form-2-ipv6_space").send_keys("256")
        self.driver.find_element_by_id("id_form-2-url").clear()
        self.driver.find_element_by_id("id_form-2-url").send_keys("http://example.com/new_offer/")
        self.driver.find_element_by_id("id_form-2-promo_code").clear()
        self.driver.find_element_by_id("id_form-2-promo_code").send_keys("CHEAP_PROMO_CODE")
        self.driver.find_element_by_id("id_form-2-cost").clear()
        self.driver.find_element_by_id("id_form-2-cost").send_keys("15.00")
        self.driver.find_element_by_id("submit-save").click()

        new_plan = Plan.objects.latest('created_at')
        self.assertEqual(new_plan.bandwidth, 600)
        self.assertEqual(new_plan.disk_space, 200)
        self.assertEqual(new_plan.memory, 256)
        self.assertEqual(new_plan.ipv4_space, 4)
        self.assertEqual(new_plan.ipv6_space, 256)
        self.assertEqual(new_plan.url, "http://example.com/new_offer/")
        self.assertEqual(new_plan.promo_code, "CHEAP_PROMO_CODE")
        self.assertEqual(new_plan.cost, 15.00)

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 3)

    def test_can_add_new_plans_out_of_order(self):
        """
        Test that the user can add new plans to an offer out of the order (with a different form field)
        """

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)

        # Send in some new data
        self.driver.find_element_by_id("id_form-3-bandwidth").clear()
        self.driver.find_element_by_id("id_form-3-bandwidth").send_keys("600")
        self.driver.find_element_by_id("id_form-3-disk_space").clear()
        self.driver.find_element_by_id("id_form-3-disk_space").send_keys("200")
        self.driver.find_element_by_id("id_form-3-memory").clear()
        self.driver.find_element_by_id("id_form-3-memory").send_keys("256")
        self.driver.find_element_by_id("id_form-3-ipv4_space").clear()
        self.driver.find_element_by_id("id_form-3-ipv4_space").send_keys("4")
        self.driver.find_element_by_id("id_form-3-ipv6_space").clear()
        self.driver.find_element_by_id("id_form-3-ipv6_space").send_keys("256")
        self.driver.find_element_by_id("id_form-3-url").clear()
        self.driver.find_element_by_id("id_form-3-url").send_keys("http://example.com/new_offer/")
        self.driver.find_element_by_id("id_form-3-promo_code").clear()
        self.driver.find_element_by_id("id_form-3-promo_code").send_keys("CHEAP_PROMO_CODE")
        self.driver.find_element_by_id("id_form-3-cost").clear()
        self.driver.find_element_by_id("id_form-3-cost").send_keys("15.00")
        self.driver.find_element_by_id("submit-save").click()

        new_plan = Plan.objects.latest('created_at')
        self.assertEqual(new_plan.bandwidth, 600)
        self.assertEqual(new_plan.disk_space, 200)
        self.assertEqual(new_plan.memory, 256)
        self.assertEqual(new_plan.ipv4_space, 4)
        self.assertEqual(new_plan.ipv6_space, 256)
        self.assertEqual(new_plan.url, "http://example.com/new_offer/")
        self.assertEqual(new_plan.promo_code, "CHEAP_PROMO_CODE")
        self.assertEqual(new_plan.cost, 15.00)

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 3)

    def test_plan_form_can_not_edit_other_plans(self):
        """
        Test that the user can not modify the form to edit plans with a different ID
        """

        another_plan = mommy.make(Plan, cost=400.00, url="http://example.com/offer")

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 2)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 3)
        self.assertEqual(self.offer.plan_set.count(), 2)

        # Update the hidden id field to that of the another_plan
        self.driver.execute_script('$("#id_form-0-id").val({0})'.format(another_plan.pk))
        self.assertEqual(self.driver.execute_script('return $("#id_form-0-id").val()'), str(another_plan.pk))

        # Set the new values for form 1
        self.driver.find_element_by_id("id_form-0-bandwidth").clear()
        self.driver.find_element_by_id("id_form-0-bandwidth").send_keys("200")
        self.driver.find_element_by_id("id_form-0-disk_space").clear()
        self.driver.find_element_by_id("id_form-0-disk_space").send_keys("100")
        self.driver.find_element_by_id("id_form-0-memory").clear()
        self.driver.find_element_by_id("id_form-0-memory").send_keys("1024")
        self.driver.find_element_by_id("id_form-0-ipv4_space").clear()
        self.driver.find_element_by_id("id_form-0-ipv4_space").send_keys("1")
        self.driver.find_element_by_id("id_form-0-ipv6_space").clear()
        self.driver.find_element_by_id("id_form-0-ipv6_space").send_keys("16")
        self.driver.find_element_by_id("id_form-0-url").clear()
        self.driver.find_element_by_id("id_form-0-url").send_keys("http://example.com/")
        self.driver.find_element_by_id("id_form-0-promo_code").clear()
        self.driver.find_element_by_id("id_form-0-promo_code").send_keys("CHEAP")
        self.driver.find_element_by_id("id_form-0-cost").clear()
        self.driver.find_element_by_id("id_form-0-cost").send_keys("400.00")

        # Submit the form
        self.driver.find_element_by_id("submit-save").click()

        # Make sure there were no errors i.e. the form still exists
        self.driver.find_element_by_id("id_form-0-bandwidth")

        # Make sure that neither model was changed
        updated_another_plan = Plan.objects.get(pk=another_plan.pk)

        self.assertEqual(updated_another_plan.bandwidth, another_plan.bandwidth)
        self.assertEqual(updated_another_plan.memory, another_plan.memory)
        self.assertEqual(updated_another_plan.offer, another_plan.offer)
        self.assertEqual(updated_another_plan.cost, another_plan.cost)

        updated_plan_1 = Plan.objects.get(pk=self.plan1.pk)

        self.assertEqual(updated_plan_1.bandwidth, 200)
        self.assertEqual(updated_plan_1.memory, 1024)
        self.assertEqual(updated_plan_1.offer, self.offer)
        self.assertEqual(updated_plan_1.cost, 400.00)
