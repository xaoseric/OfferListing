from django.conf.urls import patterns, url, include
from offers.api import OfferResource, PlanResource
from tastypie.api import Api


urlpatterns = patterns('offers.views',
    url(r'^view/(?P<offer_pk>\d+)/$', 'view_offer', name='view'),
    url(r'^view/(?P<offer_pk>\d+)-(?P<slug>[-\w]+)/$', 'view_offer', name='view_slug'),

    url(r'^providers/$', 'provider_list', name='providers'),
    url(r'^provider/(?P<provider_name>[-\w]+)/$', 'provider_profile', name='provider'),

    url(r'^manage/$', 'admin_provider_home', name="admin_home"),

    url(r'^manage/requests/$', 'admin_provider_requests', name="admin_requests"),
    url(r'^manage/request/$', 'admin_submit_request', name="admin_request_new"),
    url(r'^manage/request/(?P<request_pk>\d+)/$', 'admin_edit_request', name="admin_request_edit"),
    url(r'^manage/request/(?P<request_pk>\d+)/delete/$', 'admin_provider_delete_confirm', name="admin_request_delete"),

    url(r'^manage/offers/$', 'admin_provider_offer_list', name="admin_offers"),
    url(r'^manage/offer/(?P<offer_pk>\d+)/$', 'admin_provider_offer_edit', name="admin_offer"),
    url(r'^manage/offer/(?P<offer_pk>\d+)/mark/$', 'admin_provider_offer_mark', name="admin_offer_mark"),
    url(
        r'^manage/offer/(?P<offer_pk>\d+)/mark/(?P<plan_pk>\d+)$',
        'admin_provider_offer_plan_mark',
        name="admin_offer_plan_mark"
    ),
    url(r'^manage/offer/(?P<offer_pk>\d+)/update/$', 'admin_provider_update_offer', name="admin_offer_update"),
    url(
        r'^manage/offer/(?P<offer_pk>\d+)/update/mark/$',
        'admin_provider_update_offer_mark',
        name="admin_offer_update_mark"
    ),
    url(
        r'^manage/offer/(?P<offer_pk>\d+)/update/delete/$',
        'admin_provider_update_delete_confirm',
        name="admin_offer_update_delete"
    ),

    url(r'^manage/locations/$', 'admin_provider_locations', name="admin_locations"),
    url(r'^manage/location/(?P<location_pk>\d+)/$', 'admin_provider_locations_edit', name="admin_location_edit"),
    url(r'^manage/location/new/$', 'admin_provider_locations_new', name="admin_location_new"),

    url(r'^manage/admin/updates/$', 'superuser_approve_updates', name="superuser_approve_updates"),
)
