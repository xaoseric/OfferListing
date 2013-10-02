from tastypie.resources import ModelResource
from tastypie import fields
from offers.models import Plan, Offer, Location, Provider, Datacenter
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from django.template.loader import render_to_string


class ProviderResource(ModelResource):
    class Meta:
        queryset = Provider.objects.all()
        resource_name = 'provider'

        filtering = {
            "name": ALL,
            "id": ALL,
        }


class OfferResource(ModelResource):

    provider = fields.ForeignKey(ProviderResource, 'provider', full=True)

    class Meta:
        queryset = Offer.objects.filter(status=Offer.PUBLISHED)
        resource_name = 'offer'

        excludes = ["content"]

        filtering = {
            "name": ALL,
            "is_active": ALL,

            "provider": ALL_WITH_RELATIONS,
        }


class DatacenterResource(ModelResource):
    class Meta:
        queryset = Datacenter.objects.all()
        resource_name = 'datacenter'
        filtering = {
            "name": ALL,
            "website": ALL,
            "id": ALL,
        }


class LocationResource(ModelResource):

    datacenter = fields.ForeignKey(DatacenterResource, 'datacenter')

    class Meta:
        queryset = Location.objects.all()
        resource_name = 'location'
        filtering = {
            "country": ALL,
            "city": ALL,
            "datacenter": ALL_WITH_RELATIONS,
            "id": ALL,
        }


class PlanResource(ModelResource):

    offer = fields.ForeignKey(OfferResource, 'offer', full=True)
    location = fields.ForeignKey(LocationResource, 'location', full=True)

    html = fields.CharField()

    def dehydrate_html(self, bundle):
        return render_to_string('offers/plan_find_listing.html', {"plan": bundle.obj})

    class Meta:
        queryset = Plan.objects.filter(
            is_active=True,
            offer__status=Offer.PUBLISHED,
            offer__is_active=True,
            offer__is_request=False,
        )
        resource_name = 'plan'
        filtering = {
            "virtualization": ALL,
            "bandwidth": ALL,
            "disk_space": ALL,
            "memory": ALL,

            "ipv4_space": ALL,
            "ipv6_space": ALL,

            "billing_time": ALL,
            "url": ALL,
            "promo_code": ALL,
            "cost": ALL,

            "location": ALL_WITH_RELATIONS,
            "offer": ALL_WITH_RELATIONS,
        }

        ordering = ['bandwidth', 'disk_space', 'memory', 'ipv4_space', 'ipv6_space', 'cost', 'created_at']
