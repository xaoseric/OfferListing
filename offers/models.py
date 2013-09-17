from django.db import models


class Provider(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


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
    promo_code = models.CharField(blank=True, default='', max_length=255)
    cost = models.DecimalField(max_digits=20, decimal_places=2)
