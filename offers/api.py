from tastypie.resources import ModelResource
from tastypie import fields
from offers.models import Plan, Offer, Location
from tastypie.constants import ALL, ALL_WITH_RELATIONS


class OfferResource(ModelResource):

    class Meta:
        queryset = Offer.objects.filter(status=Offer.PUBLISHED)
        resource_name = 'offer'
        allowed_methods = ['get', 'post']



class LocationResource(ModelResource):

    class Meta:
        queryset = Location.objects.all()
        resource_name = 'location'
        allowed_methods = ['get', 'post']
        filtering = {
            "country": ALL,
            "city": ALL,
            "datacenter": ALL,
        }



class PlanResource(ModelResource):

    offer = fields.ForeignKey(OfferResource, 'offer', full=True)
    location = fields.ForeignKey(LocationResource, 'location', full=True)

    class Meta:
        queryset = Plan.objects.filter(is_active=True, offer__status=Offer.PUBLISHED, offer__is_active=True)
        resource_name = 'plan'
        filtering = {
            "bandwidth": ALL,
            "location": ALL_WITH_RELATIONS,
        }
