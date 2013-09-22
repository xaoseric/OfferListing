from django.db import models
from offers.models import Offer


class OfferRequestActiveManager(models.Manager):
    """
    The offer requests that have not yet been published
    """
    def get_query_set(self):
        return super(OfferRequestActiveManager, self).get_query_set().filter(offer__status=Offer.UNPUBLISHED)

    def get_requests_for_provider(self, provider):
        """
        Get all the requests for a specific provider
        """
        return self.get_query_set().filter(offer__provider=provider)


class OfferVisibleManager(models.Manager):
    """
    Only gets the visible offers (offers which are published)
    """
    def get_query_set(self):
        return super(OfferVisibleManager, self).get_query_set().filter(status=Offer.PUBLISHED)

    def for_provider(self, provider):
        """
        Returns all visible offers for a provider
        """
        return self.get_query_set().filter(provider=provider)


class OfferActiveManager(models.Manager):
    """
    Only gets the active offers (offers which are published and have the active status)
    """
    def get_query_set(self):
        return super(OfferActiveManager, self).get_query_set().filter(status=Offer.PUBLISHED, is_active=True)

    def for_provider(self, provider):
        """
        Returns all visible offers for a provider
        """
        return self.get_query_set().filter(provider=provider)


class ActivePlanManager(models.Manager):
    """
    A plan manager that only gets active plans
    """
    def get_query_set(self):
        return super(ActivePlanManager, self).get_query_set().filter(
            offer__status=Offer.PUBLISHED,
            offer__is_active=True,
            is_active=True
        )

    def for_provider(self, provider):
        """
        Get all the active plans (The ones that match the conditions that the offer is published, the offer is
        active and the plan is active)
        """
        return self.get_query_set().filter(offer__provider=provider)

    def for_offer(self, offer):
        """
        Get all the active plans for an offer
        """
        return self.get_query_set().filter(offer=offer)