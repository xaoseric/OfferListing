from tastypie.resources import ModelResource
from tastypie import fields
from offers.models import Plan, Offer


class OfferResource(ModelResource):

    class Meta:
        queryset = Offer.objects.filter(status=Offer.PUBLISHED)
        resource_name = 'offer'


class PlanResource(ModelResource):

    offer = fields.ForeignKey(OfferResource, 'offer')

    class Meta:
        queryset = Plan.objects.filter(is_active=True, offer__status=Offer.PUBLISHED, offer__is_active=True)
        resource_name = 'plan'