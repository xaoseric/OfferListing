from offers.models import Offer, Provider, Plan, OfferRequest, OfferUpdate, PlanUpdate
from selenium_test import SeleniumTestCase
from selenium.webdriver.common.by import By
from model_mommy import mommy
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


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

    def test_plan_form_can_delete_empty_plans(self):
        """
        Test that checking the delete box on empty plan forms does nothing (modifies no data)
        """

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(OfferRequest.objects.count(), 0)
        self.assertEqual(Plan.objects.count(), 0)

        #  Submit a new offer
        self.driver.find_element_by_id("id_name").clear()
        self.driver.find_element_by_id("id_name").send_keys("Some title")
        self.driver.find_element_by_id("id_content").clear()
        self.driver.find_element_by_id("id_content").send_keys("Some content for the new offer")
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

        # Click some delete boxes
        self.driver.find_element_by_id("id_form-2-DELETE").click()
        self.driver.find_element_by_id("id_form-3-DELETE").click()
        self.driver.find_element_by_id("submit-save").click()

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 1)

        # Make sure the page has no errors
        self.driver.find_element_by_id("id_form-0-bandwidth")


class ProviderAdminEditOfferRequestTests(SeleniumTestCase):
    def setUp(self):
        self.user = User.objects.create_user('user', 'test@example.com', 'password')
        self.provider = mommy.make(Provider)
        self.user.user_profile.provider = self.provider
        self.user.user_profile.save()

        self.offer = mommy.make(Offer, status=Offer.UNPUBLISHED, provider=self.provider)
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

    def test_plan_form_can_delete_plans(self):
        """
        Test that checking the delete box on plans deletes them
        """

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)

        self.driver.find_element_by_id("id_form-0-DELETE").click()
        self.driver.find_element_by_id("submit-save").click()

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 1)

    def test_plan_form_can_delete_multiple_plans(self):
        """
        Test that checking the delete box on plans deletes them with multiple plans
        """

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)

        self.driver.find_element_by_id("id_form-0-DELETE").click()
        self.driver.find_element_by_id("id_form-1-DELETE").click()
        self.driver.find_element_by_id("submit-save").click()

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 0)

    def test_plan_form_can_delete_empty_plans(self):
        """
        Test that checking the delete box on empty plan forms does nothing (modifies no data)
        """

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)

        self.driver.find_element_by_id("id_form-3-DELETE").click()
        self.driver.find_element_by_id("id_form-4-DELETE").click()
        self.driver.find_element_by_id("submit-save").click()

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferRequest.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)


class ProviderAdminUpdateOfferTests(SeleniumTestCase):
    def setUp(self):
        self.user = User.objects.create_user('user', 'test@example.com', 'password')
        self.provider = mommy.make(Provider)
        self.user.user_profile.provider = self.provider
        self.user.user_profile.save()

        self.offer = mommy.make(Offer, status=Offer.PUBLISHED, provider=self.provider)
        self.plan1 = mommy.make(Plan, offer=self.offer, cost=200.20, url='http://example.com/first/')
        self.plan2 = mommy.make(Plan, offer=self.offer, cost=3000.82, url='http://example.com/second/')

        self.offer_update = OfferUpdate.objects.get_update_for_offer(self.offer, self.user)

        self.login()
        self.open(reverse("offer:admin_offer_update", args=[self.offer_update.for_offer.pk]))

    def test_offer_update_form_has_correct_data(self):
        """
        Test that the offer update form contains all the correct data to update an offer
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

    def test_can_update_offer_using_form(self):
        """
        Test that a user can submit an offer update using the provided form
        """

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)
        self.assertEqual(OfferUpdate.objects.count(), 1)
        self.assertEqual(PlanUpdate.objects.count(), 2)

        # Submit the new values
        self.driver.find_element_by_id("id_name").clear()
        self.driver.find_element_by_id("id_name").send_keys("New title")
        self.driver.find_element_by_id("id_content").clear()
        self.driver.find_element_by_id("id_content").send_keys("New content")
        self.driver.find_element_by_id("submit-save").click()

        # Reload the local instances
        offer = Offer.objects.get(pk=self.offer.pk)
        offer_update = OfferUpdate.objects.get(pk=self.offer_update.pk)

        # Make sure the new data is saved to the database
        self.assertEqual(offer_update.name, "New title")
        self.assertEqual(offer_update.content, "New content")

        # Make sure initial offer has not changed
        self.assertEqual(self.offer.name, offer.name)
        self.assertEqual(self.offer.content, offer.content)

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)
        self.assertEqual(OfferUpdate.objects.count(), 1)
        self.assertEqual(PlanUpdate.objects.count(), 2)

    def test_can_update_plans_using_form(self):
        """
        Test that a user can update the plans of an offer update using the provided forms
        """

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)
        self.assertEqual(OfferUpdate.objects.count(), 1)
        self.assertEqual(PlanUpdate.objects.count(), 2)

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
        plan1 = Plan.objects.get(pk=self.plan1.pk)
        plan2 = Plan.objects.get(pk=self.plan2.pk)

        plan_update1 = PlanUpdate.objects.all()[0]
        plan_update2 = PlanUpdate.objects.all()[1]

        # Assert the data for plan update 1 is the same
        self.assertEqual(plan_update1.bandwidth, 200)
        self.assertEqual(plan_update1.disk_space, 100)
        self.assertEqual(plan_update1.memory, 1024)
        self.assertEqual(plan_update1.ipv4_space, 1)
        self.assertEqual(plan_update1.ipv6_space, 16)
        self.assertEqual(plan_update1.url, "http://example.com/")
        self.assertEqual(plan_update1.promo_code, "CHEAP")
        self.assertEqual(plan_update1.cost, 400.00)

        # Assert the data for plan update 2 is the same
        self.assertEqual(plan_update2.disk_space, 300)
        self.assertEqual(plan_update2.memory, 4096)
        self.assertEqual(plan_update2.ipv4_space, 2)
        self.assertEqual(plan_update2.ipv6_space, 32)
        self.assertEqual(plan_update2.url, "http://example.com/special/")
        self.assertEqual(plan_update2.promo_code, "")
        self.assertEqual(plan_update2.cost, 800.00)

        # Assert that the old plan values have not changes
        self.assertEqual(plan1.bandwidth, self.plan1.bandwidth)
        self.assertEqual(plan2.bandwidth, self.plan2.bandwidth)

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)
        self.assertEqual(OfferUpdate.objects.count(), 1)
        self.assertEqual(PlanUpdate.objects.count(), 2)

    def test_saving_does_not_duplicate_data(self):
        """
        Test that saving does not duplicate any database data
        """

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)
        self.assertEqual(OfferUpdate.objects.count(), 1)
        self.assertEqual(PlanUpdate.objects.count(), 2)

        self.driver.find_element_by_id("submit-save").click()

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)
        self.assertEqual(OfferUpdate.objects.count(), 1)
        self.assertEqual(PlanUpdate.objects.count(), 2)

    def test_can_add_new_plans(self):
        """
        Test that the user can add new plans to an offer update
        """

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)
        self.assertEqual(OfferUpdate.objects.count(), 1)
        self.assertEqual(PlanUpdate.objects.count(), 2)

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

        new_plan = PlanUpdate.objects.latest('created_at')
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
        self.assertEqual(Plan.objects.count(), 2)
        self.assertEqual(OfferUpdate.objects.count(), 1)
        self.assertEqual(PlanUpdate.objects.count(), 3)

    def test_can_add_new_plans_out_of_order(self):
        """
        Test that the user can add new plans to an offer out of the order (with a different form field)
        """

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)
        self.assertEqual(OfferUpdate.objects.count(), 1)
        self.assertEqual(PlanUpdate.objects.count(), 2)

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

        new_plan = PlanUpdate.objects.latest('created_at')
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
        self.assertEqual(Plan.objects.count(), 2)
        self.assertEqual(OfferUpdate.objects.count(), 1)
        self.assertEqual(PlanUpdate.objects.count(), 3)

    def test_plan_form_can_not_edit_other_plans(self):
        """
        Test that the user can not modify the form to update plans with a different ID
        """

        another_plan = mommy.make(PlanUpdate, cost=400.00, url="http://example.com/offer")

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 2)
        self.assertEqual(Plan.objects.count(), 2)
        self.assertEqual(self.offer.plan_set.count(), 2)

        self.assertEqual(OfferUpdate.objects.count(), 2)
        self.assertEqual(PlanUpdate.objects.count(), 3)
        self.assertEqual(self.offer_update.planupdate_set.count(), 2)

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
        updated_another_plan = PlanUpdate.objects.get(pk=another_plan.pk)

        self.assertEqual(updated_another_plan.bandwidth, another_plan.bandwidth)
        self.assertEqual(updated_another_plan.memory, another_plan.memory)
        self.assertEqual(updated_another_plan.offer, another_plan.offer)
        self.assertEqual(updated_another_plan.cost, another_plan.cost)

        updated_plan_1 = PlanUpdate.objects.get(pk=self.plan1.pk)

        self.assertEqual(updated_plan_1.bandwidth, 200)
        self.assertEqual(updated_plan_1.memory, 1024)
        self.assertEqual(updated_plan_1.offer, self.offer_update)
        self.assertEqual(updated_plan_1.cost, 400.00)

    def test_plan_form_can_delete_plans(self):
        """
        Test that checking the delete box on plans deletes them
        """

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)
        self.assertEqual(OfferUpdate.objects.count(), 1)
        self.assertEqual(PlanUpdate.objects.count(), 2)

        self.driver.find_element_by_id("id_form-0-DELETE").click()
        self.driver.find_element_by_id("submit-save").click()

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)
        self.assertEqual(OfferUpdate.objects.count(), 1)
        self.assertEqual(PlanUpdate.objects.count(), 1)

    def test_plan_form_can_delete_multiple_plans(self):
        """
        Test that checking the delete box on plans deletes them with multiple plans
        """

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)
        self.assertEqual(OfferUpdate.objects.count(), 1)
        self.assertEqual(PlanUpdate.objects.count(), 2)

        self.driver.find_element_by_id("id_form-0-DELETE").click()
        self.driver.find_element_by_id("id_form-1-DELETE").click()
        self.driver.find_element_by_id("submit-save").click()

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)
        self.assertEqual(OfferUpdate.objects.count(), 1)
        self.assertEqual(PlanUpdate.objects.count(), 0)

    def test_plan_form_can_delete_empty_plans(self):
        """
        Test that checking the delete box on empty plan forms does nothing (modifies no data)
        """

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)
        self.assertEqual(OfferUpdate.objects.count(), 1)
        self.assertEqual(PlanUpdate.objects.count(), 2)

        self.driver.find_element_by_id("id_form-3-DELETE").click()
        self.driver.find_element_by_id("id_form-4-DELETE").click()
        self.driver.find_element_by_id("submit-save").click()

        # Assert the correct amount of records in the database
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(Plan.objects.count(), 2)
        self.assertEqual(OfferUpdate.objects.count(), 1)
        self.assertEqual(PlanUpdate.objects.count(), 2)
