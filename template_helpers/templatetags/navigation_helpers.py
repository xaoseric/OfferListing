from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag
def navigation_link(request, url, title, active_text='active', reverse_url=True):
    link = url
    if reverse_url:
        link = reverse(url)
    active = ''
    if request.path == link:
        active = active_text

    return "<li class='{0}'><a href='{1}'>{2}</a></li>".format(active, link, title)
