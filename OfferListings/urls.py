from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'offers.views.list_offers', name='home'),
    url(r'^p(?P<page_number>\d+)/$', 'offers.views.list_offers', name='home_pagination'),
    url(r'^offers/', include('offers.urls', namespace='offer')),

    url(r'^admin/', include(admin.site.urls)),
)
