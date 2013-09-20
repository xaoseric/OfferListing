from django.contrib.auth.decorators import user_passes_test


def user_is_provider(view=None):
    actual_decorator = user_passes_test(
        lambda u: u.user_profile.provider is None,
    )
    if view:
        return actual_decorator(view)
    return actual_decorator
