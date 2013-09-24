from django.conf import settings


def footer_context_processor(request):
    if settings.FOOTER_EXTRA != '':
        return {"footer_extra": settings.FOOTER_EXTRA}
    return {"footer_extra": False}
