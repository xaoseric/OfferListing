from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.assignment_tag
def has_liked(request, comment):
    """

    :param request: The request with a user
    :type request: HttpRequest
    :param comment: The comment to check
    :return: If the user has liked a comment
    :rtype: bool
    """

    if not request.user.is_authenticated():
        return False

    return comment.does_like(request.user)
