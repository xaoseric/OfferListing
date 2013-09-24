from django.test import TestCase
from offers.models import Offer, Provider, Plan, Comment, OfferRequest, OfferUpdate, PlanUpdate
from offers.selenium_test import SeleniumTestCase
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


class ProviderAdminRequestViewTests(TestCase):
    """
    Tests that validate how the views work
    """
    def setUp(self):
        self.user = User.objects.create_user(username='user', email='person@example.com', password='password')
        self.provider = mommy.make(Provider)
        self.user.user_profile.provider = self.provider
        self.user.user_profile.save()

        self.offer = mommy.make(Offer, provider=self.provider, status=Offer.UNPUBLISHED)
        self.offer_request = OfferRequest(offer=self.offer, user=self.user)
        self.offer_request.save()

        self.client.login(username='user', password='password')

    def test_user_can_view_provider_admin_profile(self):
        """
        Test a user which manages a provider can view the provider manage page.
        """
        response = self.client.get(reverse('offer:admin_home'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.provider.name)

    def test_logged_out_user_can_not_view_provider_admin_profile(self):
        """
        Test that a user which is logged out can not view the provider admin profile
        """
        self.client.logout()

        response = self.client.get(reverse('offer:admin_home'), follow=True)

        self.assertIn(reverse('login'), response.redirect_chain[0][0])
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertEqual(response.status_code, 200)

        self.assertNotContains(response, self.provider.name)

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

    def test_user_can_modify_their_provider(self):
        """
        Test that a user can edit their own provider through the admin home page
        """

        response = self.client.get(reverse('offer:admin_home'))
        self.assertEqual(response.status_code, 200)

        # Make sure the name is present
        self.assertContains(response, self.provider.name)

        # Send off a post request
        new_data = {
            "name": 'New provider',
            "start_date": self.provider.start_date,
            "website": "http://example.com/provider/",
        }
        response = self.client.post(reverse('offer:admin_home'), new_data, follow=True)

        self.assertContains(response, 'New provider')
        self.assertContains(response, 'http://example.com/provider/')

        new_provider = Provider.objects.get(pk=self.provider.pk)
        self.assertEqual(new_provider.name, 'New provider')
        self.assertEqual(new_provider.website, 'http://example.com/provider/')

    def test_user_can_not_modify_their_provider_with_incorrect_information(self):
        """
        Test that a user can not edit their own provider through the admin home page if some information is incorrect
        """

        response = self.client.get(reverse('offer:admin_home'))
        self.assertEqual(response.status_code, 200)

        # Make sure the name is present
        self.assertContains(response, self.provider.name)

        # Send off a post request
        new_data = {
            "name": '',  # Empty name
            "start_date": self.provider.start_date,
            "website": "http://example.com/provider/",
        }
        response = self.client.post(reverse('offer:admin_home'), new_data, follow=True)

        new_provider = Provider.objects.get(pk=self.provider.pk)
        self.assertNotEqual(new_provider.name, '')
        self.assertNotEqual(new_provider.website, 'http://example.com/provider/')

        self.assertEqual(new_provider.name, self.provider.name)
        self.assertEqual(new_provider.website, self.provider.website)

    def test_user_can_view_provider_admin_new_request(self):
        """
        Test a user which manages a provider can view the provider request offer page
        """
        response = self.client.get(reverse('offer:admin_request_new'))
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_user_can_not_view_provider_admin_new_request(self):
        """
        Test a user which can not manage a provider can not access the request offer page
        """
        self.user.user_profile.provider = None
        self.user.user_profile.save()
        response = self.client.get(reverse('offer:admin_request_new'), follow=True)

        self.assertIn(reverse('login'), response.redirect_chain[0][0])
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertEqual(response.status_code, 200)

        self.assertNotContains(response, self.provider.name)

    def test_user_can_view_provider_admin_edit_request(self):
        """
        Test a user which manages a provider can view the provider edit offer request page
        """

        response = self.client.get(reverse('offer:admin_request_edit', args=[self.offer_request.pk]))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.offer.name)
        self.assertContains(response, self.offer.content)

    def test_user_can_not_view_other_provider_admin_edit_request(self):
        """
        Test a user which manages a provider can not view other providers requests
        """

        new_user = User.objects.create_user('user2', 'user2@example.com', 'password')
        offer = mommy.make(Offer, status=Offer.UNPUBLISHED)
        offer_request = OfferRequest(offer=offer, user=new_user)
        offer_request.save()

        response = self.client.get(reverse('offer:admin_request_edit', args=[offer_request.pk]))
        self.assertEqual(response.status_code, 404)

    def test_user_can_not_view_published_admin_edit_request(self):
        """
        Test a user which manages a provider can not edit an offer of theirs which is published
        """

        self.offer.status = Offer.PUBLISHED
        self.offer.save()

        response = self.client.get(reverse('offer:admin_request_edit', args=[self.offer_request.pk]))
        self.assertEqual(response.status_code, 404)

    def test_user_can_view_offer_request_list(self):
        """
        Test that a user can view the offer requests page for their own provider
        """

        response = self.client.get(reverse('offer:admin_requests'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.offer.name)
        self.assertContains(response, self.offer_request.user.username)

    def test_unauthorized_user_can_not_view_offer_request_list(self):
        """
        Test a user which can not manage a provider can not access the request offer list
        """
        self.user.user_profile.provider = None
        self.user.user_profile.save()
        response = self.client.get(reverse('offer:admin_request_new'), follow=True)

        self.assertIn(reverse('login'), response.redirect_chain[0][0])
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertEqual(response.status_code, 200)

        self.assertNotContains(response, self.provider.name)

    def test_user_can_view_offer_request_list_only_of_self(self):
        """
        Test that a user can view the offer requests page for their own provider, and no-one else
        """

        other_requests = mommy.make(OfferRequest, _quantity=10)

        response = self.client.get(reverse('offer:admin_requests'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.offer.name)
        self.assertContains(response, self.offer_request.user.username)

        for other_request in other_requests:
            self.assertNotContains(response, other_request.offer.name)
            self.assertNotContains(response, other_request.user.username)

    def test_user_can_view_delete_request(self):
        """
        Test that a user can view the delete page for a request of their provider
        """

        plans = mommy.make(Plan, _quantity=4, offer=self.offer_request.offer)

        response = self.client.get(reverse('offer:admin_request_delete', args=[self.offer_request.pk]))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.offer.name)

        for plan in plans:
            self.assertContains(response, plan.get_memory())

    def test_user_can_perform_delete_request(self):
        """
        Test that a user can perform the delete of a request of their provider
        """

        plans = mommy.make(Plan, _quantity=4, offer=self.offer_request.offer)

        response = self.client.get(
            reverse('offer:admin_request_delete', args=[self.offer_request.pk]) + '?delete=True',
            follow=True
        )

        self.assertIn(reverse('offer:admin_requests'), response.redirect_chain[0][0])
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertEqual(response.status_code, 200)

        self.assertNotContains(response, self.offer.name)

        # Assert the plans, offer and offer request no longer exist
        self.assertFalse(Offer.objects.filter(pk=self.offer.pk).exists())
        self.assertFalse(OfferRequest.objects.filter(pk=self.offer_request.pk).exists())

        for plan in plans:
            self.assertFalse(Plan.objects.filter(pk=plan.pk).exists())

    def test_unauthorized_user_can_not_view_delete_request(self):
        """
        Test a user which can not manage a provider can not access the request delete page
        """
        self.user.user_profile.provider = None
        self.user.user_profile.save()
        response = self.client.get(reverse('offer:admin_request_delete', args=[self.offer_request.pk]), follow=True)

        self.assertIn(reverse('login'), response.redirect_chain[0][0])
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertEqual(response.status_code, 200)

        self.assertNotContains(response, self.provider.name)


class ProviderAdminOfferViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', email='person@example.com', password='password')
        self.provider = mommy.make(Provider)
        self.user.user_profile.provider = self.provider
        self.user.user_profile.save()

        self.offer = mommy.make(Offer, provider=self.provider, status=Offer.UNPUBLISHED)

        self.client.login(username='user', password='password')

    def test_user_can_view_offer_list(self):
        """
        Test that a user can view their own offer list
        """

        offers = mommy.make(Offer, provider=self.provider, _quantity=20)

        response = self.client.get(reverse('offer:admin_offers'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(self.provider, response.context["provider"])

        for offer in offers:
            self.assertIn(offer, response.context["offers"])

    def test_offer_list_does_not_contain_offer_requests(self):
        """
        Test that the offer list does not contain offer requests
        """
        offers = mommy.make(Offer, provider=self.provider, _quantity=20)
        offer_requests = mommy.make(
            OfferRequest,
            offer__provider=self.provider,
            offer__status=Offer.UNPUBLISHED,
            _quantity=20
        )

        response = self.client.get(reverse('offer:admin_offers'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(self.provider, response.context["provider"])

        for offer in offers:
            self.assertIn(offer, response.context["offers"])

        for offer_request in offer_requests:
            self.assertNotIn(offer_request, response.context["offers"])

    def test_user_can_mark_offer_as_active(self):
        """
        Test that a user can mark their own offer as active
        """
        self.offer.is_active = False
        self.offer.save()

        response = self.client.get(reverse('offer:admin_offer_mark', args=[self.offer.pk]), follow=True)

        self.assertEqual(response.status_code, 200)

        updated_offer = Offer.objects.get(pk=self.offer.pk)
        self.assertTrue(updated_offer.is_active)

    def test_user_can_mark_offer_as_inactive(self):
        """
        Test that a user can mark their own offer as inactive
        """
        self.offer.is_active = True
        self.offer.save()

        response = self.client.get(reverse('offer:admin_offer_mark', args=[self.offer.pk]), follow=True)

        self.assertEqual(response.status_code, 200)

        updated_offer = Offer.objects.get(pk=self.offer.pk)
        self.assertFalse(updated_offer.is_active)

    def test_user_can_not_mark_other_offer(self):
        """
        Test that a user can not mark an offer that is not theirs (the provider is not their provider)
        """
        new_offer = mommy.make(Offer, is_active=True)

        response = self.client.get(reverse('offer:admin_offer_mark', args=[new_offer.pk]), follow=True)

        self.assertEqual(response.status_code, 404)

        updated_offer = Offer.objects.get(pk=new_offer.pk)
        self.assertTrue(updated_offer.is_active)

    def test_user_can_not_mark_offer_request(self):
        """
        Test that a user can not mark an offer request's status
        """
        offer_request = OfferRequest(offer=self.offer, user=self.user)
        offer_request.save()

        response = self.client.get(reverse('offer:admin_offer_mark', args=[self.offer.pk]), follow=True)

        self.assertEqual(response.status_code, 404)

        updated_offer = Offer.objects.get(pk=self.offer.pk)
        self.assertTrue(updated_offer.is_active)

    def test_user_can_mark_plan_as_active(self):
        """
        Test that a user can mark their own plan as active
        """
        plan = mommy.make(Plan, offer=self.offer, is_active=False)

        response = self.client.get(
            reverse('offer:admin_offer_plan_mark', args=[self.offer.pk, plan.pk]),
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('offer:admin_offer', args=[self.offer.pk]))

        updated_plan = Plan.objects.get(pk=plan.pk)
        self.assertTrue(updated_plan.is_active)

    def test_user_can_mark_plan_as_inactive(self):
        """
        Test that a user can mark their own plan as inactive
        """
        plan = mommy.make(Plan, offer=self.offer, is_active=True)

        response = self.client.get(
            reverse('offer:admin_offer_plan_mark', args=[self.offer.pk, plan.pk]),
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('offer:admin_offer', args=[self.offer.pk]))

        updated_plan = Plan.objects.get(pk=plan.pk)
        self.assertFalse(updated_plan.is_active)

    def test_user_can_not_mark_other_offer_plan(self):
        """
        Test that a user can not mark an offer plan that is not theirs (the provider is not their provider)
        """
        new_offer = mommy.make(Offer, is_active=True)
        plan = mommy.make(Plan, offer=new_offer, is_active=True)

        response = self.client.get(reverse('offer:admin_offer_plan_mark', args=[new_offer.pk, plan.pk]), follow=True)

        self.assertEqual(response.status_code, 404)

        updated_plan = Plan.objects.get(pk=plan.pk)
        self.assertTrue(updated_plan.is_active)

    def test_user_can_not_mark_non_existent_plan(self):
        """
        Test that a user can not mark a plan that is not part of their offer
        """
        plan = mommy.make(Plan, is_active=True)

        response = self.client.get(reverse('offer:admin_offer_plan_mark', args=[self.offer.pk, plan.pk]), follow=True)

        self.assertEqual(response.status_code, 404)

        updated_plan = Plan.objects.get(pk=plan.pk)
        self.assertTrue(updated_plan.is_active)

    def test_user_can_not_mark_offer_request_plan(self):
        """
        Test that a user can not mark an offer request's plan status
        """
        offer_request = OfferRequest(offer=self.offer, user=self.user)
        offer_request.save()

        plan = mommy.make(Plan, offer=self.offer, is_active=True)

        response = self.client.get(reverse('offer:admin_offer_plan_mark', args=[self.offer.pk, plan.pk]), follow=True)

        self.assertEqual(response.status_code, 404)

        updated_plan = Plan.objects.get(pk=plan.pk)
        self.assertTrue(updated_plan.is_active)

    def test_user_can_view_offer_edit_page(self):
        """
        Test that a user can view the offer edit page for one of their offers
        """

        mommy.make(Plan, offer=self.offer, _quantity=5)

        response = self.client.get(reverse('offer:admin_offer', args=[self.offer.pk]))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["offer"], self.offer)
        self.assertQuerysetEqual(response.context["plans"], map(repr, self.offer.plan_set.all()), ordered=False)

    def test_user_can_not_view_offer_edit_page_request(self):
        """
        Test that the user can not view an offer request through the offer edit page
        """
        self.offer.status = Offer.UNPUBLISHED
        self.offer.save()
        mommy.make(OfferRequest, offer=self.offer)

        response = self.client.get(reverse('offer:admin_offer', args=[self.offer.pk]))
        self.assertEqual(response.status_code, 404)

    def test_user_can_not_view_offer_edit_page_of_other_provider(self):
        """
        Test that the user can not edit an offer from another provider
        """

        other_offer = mommy.make(Offer)

        response = self.client.get(reverse('offer:admin_offer', args=[other_offer.pk]))
        self.assertEqual(response.status_code, 404)

    def test_user_can_not_view_offer_update_page_of_other_provider(self):
        """
        Test that the user can not update an offer from another provider
        """

        other_offer = mommy.make(Offer)

        response = self.client.get(reverse('offer:admin_offer_update', args=[other_offer.pk]))
        self.assertEqual(response.status_code, 404)
