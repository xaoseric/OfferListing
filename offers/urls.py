from django.conf.urls import patterns, url


urlpatterns = patterns('offers.views',
    url(r'^view/(?P<offer_pk>\d+)/$', 'view_offer', name='view'),

    url(r'^providers/$', 'provider_list', name='providers'),
    url(r'^provider/(?P<provider_pk>\d+)/$', 'provider_profile', name='provider'),
    url(r'^provider/(?P<provider_pk>\d+)/p(?P<page_number>\d+)/$', 'provider_profile', name='provider_pagination'),

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
)
