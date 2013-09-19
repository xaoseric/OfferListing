from django.conf.urls import patterns, url


urlpatterns = patterns('accounts.views',
    url(r'^login/$', 'login', name='login'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^logout/$', 'logout_then_login', name='logout'),
)
