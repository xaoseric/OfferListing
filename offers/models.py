from django.db import models
from django.core.validators import URLValidator
from django.utils.text import slugify
from django.core.urlresolvers import reverse


class Provider(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    website = models.URLField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name


class Offer(models.Model):
    PUBLISHED = 'p'
    UNPUBLISHED = 'u'
    DRAFT = 'd'

    STATUS_CHOICES = (
        (PUBLISHED, 'Published'),
        (UNPUBLISHED, 'Unpublished'),
        (DRAFT, 'Draft'),
    )

    name = models.CharField(max_length=255)
    content = models.TextField()
    provider = models.ForeignKey(Provider)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=DRAFT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def slug(self):
        return "{0}-{1}".format(self.pk, slugify(self.name))

    def __unicode__(self):
        return "{0} ({1})".format(self.name, self.provider.name)

    def get_absolute_url(self):
        return reverse('offer:view', args=[self.pk])


class Plan(models.Model):
    KVM = 'k'
    OPENVZ = 'o'

    VIRT_CHOICES = (
        (KVM, 'KVM'),
        (OPENVZ, 'OpenVZ'),
    )

    MONTHLY = 'm'
    QUARTERLY = 'q'
    YEARLY = 'y'
    BIYEARLY = 'b'

    BILLING_CHOICES = (
        (MONTHLY, 'Monthly'),
        (QUARTERLY, 'Quarterly'),
        (YEARLY, 'Yearly'),
        (BIYEARLY, 'Biyearly'),
    )

    offer = models.ForeignKey(Offer)
    virtualization = models.CharField(max_length=1, choices=VIRT_CHOICES, default=OPENVZ)

    # Data attributes
    bandwidth = models.BigIntegerField()  # In gigabytes
    disk_space = models.BigIntegerField()  # In gigabytes
    memory = models.BigIntegerField()  # In megabytes

    # Ip space
    ipv4_space = models.IntegerField()
    ipv6_space = models.IntegerField()

    # Billing details
    billing_time = models.CharField(max_length=1, choices=BILLING_CHOICES, default=MONTHLY)
    url = models.TextField(validators=[URLValidator()])
    promo_code = models.CharField(blank=True, default='', max_length=255)
    cost = models.DecimalField(max_digits=20, decimal_places=2)

    def data_format(self, value, format_type):
        """
        Format data such as MB or GB into better format. This means that:

        1024 MB -> 1 GB
        1024 GB -> 1 TB
        2048 GB -> 2 GB

        It will also only format perfect values

        2050 GB -> 2050 GB

        """
        return_string = ''
        if format_type == 'megabytes':
            if value % 1024 == 0:
                return_string = str(value / 1024) + " GB"
            else:
                return_string = str(value) + " MB"
        elif format_type == 'gigabytes':
            if value % 1024 == 0:
                return_string = str(value / 1024) + " TB"
            else:
                return_string = str(value) + " GB"
        return return_string

    def get_memory(self):
        """
        Get the pretty version of the system memory
        """
        return self.data_format(self.memory, 'megabytes')

    def get_hdd(self):
        """
        Get the pretty version of the system hdd space
        """
        return self.data_format(self.disk_space, 'gigabytes')

    def get_bandwidth(self):
        """
        Get the pretty version of the system bandwidth
        """
        return self.data_format(self.bandwidth, 'gigabytes')