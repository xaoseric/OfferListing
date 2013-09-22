from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.core.validators import URLValidator
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
import os
import uuid
from easy_thumbnails.files import get_thumbnailer
from django.utils import timezone

############
# Managers #
############


class OfferRequestActiveManager(models.Manager):
    """
    The offer requests that have not yet been published
    """
    def get_query_set(self):
        return super(OfferRequestActiveManager, self).get_query_set().filter(offer__status=Offer.UNPUBLISHED)

    def get_requests_for_provider(self, provider):
        """
        Get all the requests for a specific provider
        """
        return self.get_query_set().filter(offer__provider=provider)


class OfferNotRequestManager(models.Manager):
    """
    The offers that are not requests
    """
    def get_query_set(self):
        return super(OfferNotRequestManager, self).get_query_set().filter(
            Q(status=Offer.PUBLISHED) |
            (Q(request=None) & Q(status=Offer.UNPUBLISHED))
        )

    def for_provider(self, provider):
        """
        Get all the offers for a provider that are not requests
        """
        return self.get_query_set().filter(provider=provider)


class OfferVisibleManager(models.Manager):
    """
    Only gets the visible offers (offers which are published)
    """
    def get_query_set(self):
        return super(OfferVisibleManager, self).get_query_set().filter(status=Offer.PUBLISHED)

    def for_provider(self, provider):
        """
        Returns all visible offers for a provider
        """
        return self.get_query_set().filter(provider=provider)


class OfferActiveManager(models.Manager):
    """
    Only gets the active offers (offers which are published and have the active status)
    """
    def get_query_set(self):
        return super(OfferActiveManager, self).get_query_set().filter(status=Offer.PUBLISHED, is_active=True)

    def for_provider(self, provider):
        """
        Returns all visible offers for a provider
        """
        return self.get_query_set().filter(provider=provider)


class ActivePlanManager(models.Manager):
    """
    A plan manager that only gets active plans
    """
    def get_query_set(self):
        return super(ActivePlanManager, self).get_query_set().filter(
            offer__status=Offer.PUBLISHED,
            offer__is_active=True,
            is_active=True
        )

    def for_provider(self, provider):
        """
        Get all the active plans (The ones that match the conditions that the offer is published, the offer is
        active and the plan is active)
        """
        return self.get_query_set().filter(offer__provider=provider)

    def for_offer(self, offer):
        """
        Get all the active plans for an offer
        """
        return self.get_query_set().filter(offer=offer)


##########
# Models #
##########


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('provider_logos', filename)


class Provider(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    website = models.URLField(max_length=255)
    logo = models.ImageField(upload_to=get_file_path, blank=True, max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    def get_image_url(self):
        """
        Get the url of the providers logo. This defaults to a no_logo.png static image if the logo for the provider
        is not set.

        The dimensions of the image are 400 by 400.
        """
        if self.logo == '' or self.logo is None:
            return settings.STATIC_URL + 'img/no_logo.png'

        options = {'size': (400, 400), 'crop': True}
        return get_thumbnailer(self.logo).get_thumbnail(options).url

    def offer_count(self):
        """
        Gets the total count of all the offers related to this provider. It only returns the number of published
        offers (Offers with the status of PUBLISHED).
        """
        return Offer.visible_offers.for_provider(self).count()

    def active_offer_count(self):
        """
        Gets the total count of all the offers related to this provider. It only returns the number of published
        offers (Offers with the status of PUBLISHED) that are active.
        """
        return Offer.active_offers.for_provider(self).count()

    def plan_count(self):
        """
        Returns the number of plans this provider has associated. It only returns plans related to a published article
        (and article with the status PUBLISHED).
        """
        return Plan.active_plans.for_provider(self).count()


class OfferRequest(models.Model):
    offer = models.OneToOneField('Offer', related_name='request')
    user = models.ForeignKey(User)

    objects = models.Manager()
    requests = OfferRequestActiveManager()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OfferBase(models.Model):
    PUBLISHED = 'p'
    UNPUBLISHED = 'u'

    STATUS_CHOICES = (
        (PUBLISHED, 'Published'),
        (UNPUBLISHED, 'Unpublished'),
    )

    name = models.CharField(max_length=255)
    content = models.TextField()
    provider = models.ForeignKey(Provider)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PUBLISHED)
    is_active = models.BooleanField(default=True)

    published_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    visible_offers = OfferVisibleManager()
    active_offers = OfferActiveManager()

    class Meta:
        abstract = True


class Offer(OfferBase):

    objects = models.Manager()
    not_requests = OfferNotRequestManager()

    def __unicode__(self):
        return "{0} ({1})".format(self.name, self.provider.name)

    def get_absolute_url(self):
        """
        Returns the absolute url of the offer. This is a link to the page about the offer.
        """
        return reverse('offer:view', args=[self.pk])

    def get_comments(self):
        """
        Returns a queryset of all the **PUBLISHED** comments related to this offer. The queryset is ordered by when
        it was first created.
        """
        return self.comment_set.filter(status=Comment.PUBLISHED).order_by('created_at')

    def active_plan_count(self):
        """
        Returns the number of active plans that this offer has.
        """
        return Plan.active_plans.for_offer(self).count()

    def plan_count(self):
        """
        Returns the number of plans that this offer has.
        """
        return self.plan_set.count()

    def min_cost(self):
        """
        Returns the cost of the cheapest plan related to this offer. The return is a Decimal object.
        """
        return self.plan_set.all().aggregate(cost=models.Min('cost'))["cost"]

    def max_cost(self):
        """
        Returns the cost of the most expensive plan related to this offer. The return is a Decimal object.
        """
        return self.plan_set.all().aggregate(cost=models.Max('cost'))["cost"]

    def offer_active(self):
        """
        Returns if the offer is active
        """
        if self.is_active and self.status == self.PUBLISHED:
            return True
        return False

    def is_request(self):
        try:
            if self.request is not None and self.status == self.UNPUBLISHED:
                return True
        except OfferRequest.DoesNotExist:
            pass
        return False
    is_request.boolean = True

    class Meta:
        ordering = ['-published_at']


class OfferUpdate(OfferBase):
    for_offer = models.OneToOneField(Offer)
    user = models.ForeignKey(User)


def offer_update_published(sender, instance, raw, **kwargs):
    if instance.pk is not None:
        if instance.status == Offer.PUBLISHED:
            old_instance = Offer.objects.get(pk=instance.pk)
            if old_instance.status == Offer.UNPUBLISHED:
                instance.published_at = timezone.now()


pre_save.connect(offer_update_published, sender=Offer)


class PlanBase(models.Model):
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
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    active_plans = ActivePlanManager()

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

    def plan_active(self):
        """
        Check if the current plan is active
        """
        if self.offer.offer_active() and self.is_active:
            return True
        return False

    def __unicode__(self):
        return "{} ({})".format(self.offer.name, self.get_memory())

    class Meta:
        abstract = True


class Plan(PlanBase):
    offer = models.ForeignKey(Offer)


class PlanUpdate(PlanBase):
    offer = models.ForeignKey(OfferUpdate)
    plan = models.OneToOneField(Plan, blank=True, null=True)


class Comment(models.Model):
    PUBLISHED = 'p'
    UNPUBLISHED = 'u'
    DELETED = 'd'

    STATE_CHOICES = (
        (PUBLISHED, 'Published'),
        (UNPUBLISHED, 'Unpublished'),
        (DELETED, 'Deleted'),
    )

    commenter = models.ForeignKey(User)
    offer = models.ForeignKey(Offer)

    content = models.TextField()
    status = models.CharField(max_length=1, choices=STATE_CHOICES, default=PUBLISHED)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
