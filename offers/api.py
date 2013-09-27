from tastypie.resources import ModelResource
from tastypie import fields
from offers.models import Plan, Offer, Location


class OfferResource(ModelResource):

    class Meta:
        queryset = Offer.objects.filter(status=Offer.PUBLISHED)
        resource_name = 'offer'


class LocationResource(ModelResource):

    class Meta:
        queryset = Location.objects.all()


class PlanResource(ModelResource):

    offer = fields.ForeignKey(OfferResource, 'offer', full=True)
    location = fields.ForeignKey(LocationResource, 'location', full=True)

    class Meta:
        queryset = Plan.objects.filter(is_active=True, offer__status=Offer.PUBLISHED, offer__is_active=True)
        resource_name = 'plan'
