from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """
    
    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        
        # append a group for "Administration" & "Applications"
        self.children.append(modules.Group(
            _('Site Administration'),
            column=1,
            collapsible=True,
            children = [
                modules.ModelList(
                    _('User Management'),
                    column=1,
                    collapsible=True,
                    models=('django.contrib.auth.*', ),
                ),
                modules.ModelList(
                    _('Site Management'),
                    column=1,
                    css_classes=('collapse closed',),
                    models=('django.contrib.sites.*', 'django.contrib.flatpages.*',),
                )
            ]
        ))

        self.children.append(modules.Group(
            _('Offer Administration'),
            column=1,
            collapsible=True,
            children = [
                modules.ModelList(
                    _('Offer Details'),
                    column=1,
                    collapsible=True,
                    models=(
                        'offers.models.Provider',
                        'offers.models.Offer',
                        'offers.models.Plan',
                        'offers.models.Comment'
                    ),
                ),
                modules.ModelList(
                    _('Locations'),
                    column=1,
                    css_classes=('collapse closed',),
                    models=('offers.models.Location', 'offers.models.Datacenter',),
                )
            ]
        ))
        
        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Media Management'),
            column=2,
            children=[
                {
                    'title': _('FileBrowser'),
                    'url': '/admin/filebrowser/browse/',
                    'external': False,
                },
            ]
        ))
        
        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Support'),
            column=2,
            children=[
                {
                    'title': _('Django Documentation'),
                    'url': 'http://docs.djangoproject.com/',
                    'external': True,
                },
                {
                    'title': _('Grappelli Documentation'),
                    'url': 'http://packages.python.org/django-grappelli/',
                    'external': True,
                },
                {
                    'title': _('Grappelli Google-Code'),
                    'url': 'http://code.google.com/p/django-grappelli/',
                    'external': True,
                },
            ]
        ))
        
        # append a feed module
        self.children.append(modules.Feed(
            _('Latest Django News'),
            column=2,
            feed_url='http://www.djangoproject.com/rss/weblog/',
            limit=5
        ))
        
        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=5,
            collapsible=False,
            column=3,
        ))


