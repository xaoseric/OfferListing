from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import models
from offers.models import Provider


class UserProfile(models.Model):
    birthday = models.DateField(blank=True, null=True)
    user = models.OneToOneField(User, related_name='user_profile')
    provider = models.OneToOneField(Provider, blank=True, null=True, related_name="owners")

    def __unicode__(self):
        return "{0} profile".format(self.user.username)

    def is_provider(self):
        return self.provider is not None


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            if instance.user_profile is None:
                UserProfile.objects.create(user=instance)
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
