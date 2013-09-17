from django.conf.urls import patterns, url


urlpatterns = patterns('offers.views',
    url(r'^view/(?P<offer_pk>\d+)/$', 'offer', name='view'),
)
