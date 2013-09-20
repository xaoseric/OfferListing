from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import models


class UserProfile(models.Model):
    birthday = models.DateField(blank=True, null=True)
    user = models.OneToOneField(User)


def create_user_profile(sender, instance, created, **kwargs):
    print sender, instance, created, kwargs
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
