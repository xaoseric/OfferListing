from django.db import models
from django.db.models.signals import post_save
from django.contrib.flatpages.models import FlatPage


class FlatpageNavbar(models.Model):
    navbar_name = models.CharField(max_length=255)
    flatpage = models.OneToOneField(FlatPage)


def check_navbar(sender, instance, created, **kwargs):
    try:
        return instance.flatpagenavbar
    except FlatpageNavbar.DoesNotExist:
        FlatpageNavbar(navbar_name='', flatpage=instance).save()

post_save.connect(check_navbar, sender=FlatPage)