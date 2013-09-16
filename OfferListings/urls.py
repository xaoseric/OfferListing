from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'OfferListings.views.home', name='home'),
    # url(r'^OfferListings/', include('OfferListings.foo.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
