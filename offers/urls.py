from django.conf.urls import patterns, url


urlpatterns = patterns('offers.views',
    url(r'^view/(?P<offer_pk>\d+)/$', 'view_offer', name='view'),

    url(r'^providers/$', 'provider_list', name='providers'),
    url(r'^provider/(?P<provider_pk>\d+)/$', 'provider_profile', name='provider'),
)
