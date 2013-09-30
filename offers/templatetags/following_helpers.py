from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag
def following(request, offer):
    if not request.user.is_authenticated():
        return ""

    if not offer.followers.filter(pk=request.user.pk).exists():
        return '<a class="btn btn-success" href="%s">Follow</a>' % (offer.get_absolute_url() + '?do=follow')

    return '<a class="btn btn-warning" href="%s">Unfollow</a>' % (offer.get_absolute_url() + '?do=unfollow')
