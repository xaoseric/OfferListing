from tastypie.resources import ModelResource
from offers.models import Plan, Offer


class PlanResource(ModelResource):
    class Meta:
        queryset = Plan.objects.filter(is_active=True, offer__status=Offer.PUBLISHED, offer__is_active=True)
        resource_name = 'plan'