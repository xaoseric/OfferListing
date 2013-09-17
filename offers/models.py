from django.db import models


class Provider(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

