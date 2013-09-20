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


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
