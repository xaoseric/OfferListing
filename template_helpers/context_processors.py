from django.conf import settings


def footer_context_processor(request):
    if settings.FOOTER_EXTRA != '':
        return {"footer_extra": settings.FOOTER_EXTRA}
    return {"footer_extra": False}


def testing_mode(request):
    if settings.IS_TEST:
        return {"is_test": True}
    return {"is_test": False}
