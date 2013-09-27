from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

from offers.api import OfferResource, PlanResource
from tastypie.api import Api
admin.autodiscover()

main_api = Api(api_name='main')
main_api.register(OfferResource())
main_api.register(PlanResource())

urlpatterns = patterns('',
    url(r'^$', 'offers.views.list_offers', name='home'),
    url(r'^p(?P<page_number>\d+)/$', 'offers.views.list_offers', name='home_pagination'),

    url(r'^offers/', include('offers.urls', namespace='offer')),
    url(r'^find/data/', include(main_api.urls)),

    url(r'^accounts/', include('accounts.urls')),
    url(r'^captcha/', include('captcha.urls')),

    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
