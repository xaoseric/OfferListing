from django.conf.urls import patterns, url
from accounts.forms import BetterAuthenticationForm


urlpatterns = patterns('accounts.views',
    #url(r'^login/$', 'login', name='login'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(
        r'login/',
        'login',
        {"authentication_form": BetterAuthenticationForm, "template_name": "accounts/login.html"},
        name='login'
    ),
    url(r'^logout/$', 'logout_then_login', name='logout'),
)
