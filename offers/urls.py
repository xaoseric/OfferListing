from django.conf.urls import patterns, url


urlpatterns = patterns('offers.views',
    url(r'^view/(?P<offer_pk>\d+)/$', 'view_offer', name='view'),

    url(r'^providers/$', 'provider_list', name='providers'),
    url(r'^provider/(?P<provider_pk>\d+)/$', 'provider_profile', name='provider'),
    url(r'^provider/(?P<provider_pk>\d+)/p(?P<page_number>\d+)/$', 'provider_profile', name='provider_pagination'),

    url(r'^manage/$', 'admin_provider_home', name="admin_home"),
    url(r'^manage/request/$', 'admin_submit_request', name="admin_request_new")
)
