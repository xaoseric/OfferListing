TRACKING_CODE = """

"""

from django import template
from django.conf import settings
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag
def load_piwik_tracking():
    url = getattr(settings, 'PIWIK_URL', False)
    if not url:
        return ""

    site_id = getattr(settings, 'PIWIK_ID', 1)

    return render_to_string('template_helpers/piwik_code.html', {
        "site_id": site_id,
        "site_url": url,
    })
