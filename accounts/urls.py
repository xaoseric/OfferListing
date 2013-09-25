from django.conf.urls import patterns, url
from accounts.forms import BetterAuthenticationForm


urlpatterns = patterns('accounts.views',
    url(r'^register/$', 'register', name='register'),
    url(r'^profile/$', 'self_profile', name='self_profile'),
    url(r'^user/(?P<username>[\w.@+-]+)/$', 'profile', name='profile'),
    url(r'^profile/comments/$', 'comment_list', name='my_comments'),
    url(r'^update/$', 'edit_account', name='edit_account'),
    url(r'^update/password/$', 'change_password', name='change_password'),
    url(r'^deactivate/$', 'deactivate_account', name='deactivate_account'),
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
