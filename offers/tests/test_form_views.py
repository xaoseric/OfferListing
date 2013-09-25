from django_webtest import WebTest
from model_mommy import mommy
from offers.models import User, Provider, Offer, OfferRequest, Plan
from django.core.urlresolvers import reverse


class OfferRequestTests(WebTest):
    def setUp(self):
        self.user = User.objects.create_user('user', 'test@example.com', 'password')
        self.provider = mommy.make(Provider)
        self.user.user_profile.provider = self.provider
        self.user.user_profile.save()

    def test_form_has_correct_fields(self):
        response = self.app.get(reverse('offer:admin_request_new'), user=self.user)
        form = response.form
        form["plan_set-0-virtualization"] = Plan.OPENVZ
        response = form.submit()
        print response

