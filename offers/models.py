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
from django.utils.text import slugify
from template_helpers.cleaners import clean, super_clean
from django_countries import CountryField
import json

############
# Managers #
############


class OfferNotRequestManager(models.Manager):
    """
    The offers that are not requests
    """
    def get_query_set(self):
        return super(OfferNotRequestManager, self).get_query_set().filter(is_request=False)

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
        return super(OfferVisibleManager, self).get_query_set().filter(status=Offer.PUBLISHED, is_request=False)

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
        return super(OfferActiveManager, self).get_query_set().filter(
            status=Offer.PUBLISHED,
            is_active=True,
            is_request=False,
        )

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
            offer__is_request=False,
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
    name = models.CharField(max_length=250, unique=True)
    name_slug = models.SlugField(max_length=255, unique=True, editable=False)

    start_date = models.DateField()
    website = models.URLField(max_length=255)
    logo = models.ImageField(upload_to=get_file_path, blank=True, max_length=255)
    tos = models.URLField(max_length=255, verbose_name='Terms of service')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('offer:provider', args=[self.name_slug])

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

    def get_small_image_url(self):
        """
        Get the url of the providers small logo. This defaults to a no_logo.png static image if the logo for the
        provider is not set.

        The dimensions of the image are 200 by 200.
        """
        if self.logo == '' or self.logo is None:
            return settings.STATIC_URL + 'img/no_logo.png'

        options = {'size': (200, 200), 'crop': True}
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

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.name_slug = slugify(self.name)
        super(Provider, self).save(force_insert, force_update, using, update_fields)


class Location(models.Model):
    city = models.CharField(max_length=255)
    country = CountryField()
    datacenter = models.CharField(max_length=255)

    provider = models.ForeignKey(Provider, related_name='locations')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}, {1}".format(self.city, self.country.name.__unicode__())


class TestIP(models.Model):
    IPV4 = 'v4'
    IPV6 = 'v6'

    IP_TYPES = (
        (IPV4, 'IPv4'),
        (IPV6, 'IPv6'),
    )

    location = models.ForeignKey(Location, related_name='test_ips')
    ip_type = models.CharField(max_length=2, choices=IP_TYPES)
    ip = models.GenericIPAddressField(verbose_name='IP Address')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TestDownload(models.Model):
    location = models.ForeignKey(Location, related_name='test_downloads')
    url = models.URLField(max_length=255)
    size = models.BigIntegerField()  # In Megabytes

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

    is_request = models.BooleanField(default=False)
    creator = models.ForeignKey(User, null=True, blank=True)

    def __unicode__(self):
        return "{0} ({1})".format(self.name, self.provider.name)

    def get_absolute_url(self):
        """
        Returns the absolute url of the offer. This is a link to the page about the offer.
        """
        return reverse('offer:view_slug', args=[self.pk, slugify(self.name)])

    def get_comments(self):
        """
        Returns a queryset of all the **PUBLISHED** comments related to this offer. The queryset is ordered by when
        it was first created.
        """
        return self.comment_set.filter(status=Comment.PUBLISHED).order_by('created_at')

    def comment_count(self):
        return self.get_comments().count()

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

    def queue_position(self):
        if not self.is_request:
            return 0
        return Offer.objects.filter(
            status=Offer.UNPUBLISHED, created_at__lt=self.created_at, is_request=True
        ).count()+1

    def update_request(self):
        try:
            return self.offerupdate
        except OfferUpdate.DoesNotExist:
            return False

    def get_plan_locations(self):
        locations = []
        for plan in self.plan_set.all():
            if plan.location not in locations:
                locations.append(plan.location)
        return locations

    def from_offer_update(self, offer_update):
        self.name = offer_update.name
        self.content = offer_update.content
        self.save()
        self.plan_set.all().delete()
        for plan in offer_update.planupdate_set.all():
            new_plan = Plan(
                offer=self,
                virtualization=plan.virtualization,
                location=plan.location,

                # Data attributes
                bandwidth=plan.bandwidth,
                disk_space=plan.disk_space,
                memory=plan.memory,

                # Ip space
                ipv4_space=plan.ipv4_space,
                ipv6_space=plan.ipv6_space,

                # Billing details
                billing_time=plan.billing_time,
                url=plan.url,
                promo_code=plan.promo_code,
                cost=plan.cost,
                is_active=plan.is_active,
            )
            new_plan.save()

    class Meta:
        ordering = ['-published_at']


class OfferUpdateManager(models.Manager):
    def get_update_for_offer(self, offer, user):
        try:
            return offer.offerupdate
        except OfferUpdate.DoesNotExist:
            # Create a new offer update
            offer_update = OfferUpdate(
                for_offer=offer,
                user=user,
                name=offer.name,
                content=offer.content,
                provider=offer.provider,
                status=offer.status,
                is_active=offer.is_active,
            )
            offer_update.save()

            for plan in offer.plan_set.all():
                new_plan = PlanUpdate(
                    offer=offer_update,
                    plan=plan,

                    virtualization=plan.virtualization,
                    location=plan.location,

                    # Data attributes
                    bandwidth=plan.bandwidth,
                    disk_space=plan.disk_space,
                    memory=plan.memory,

                    # Ip space
                    ipv4_space=plan.ipv4_space,
                    ipv6_space=plan.ipv6_space,

                    # Billing details
                    billing_time=plan.billing_time,
                    url=plan.url,
                    promo_code=plan.promo_code,
                    cost=plan.cost,
                    is_active=plan.is_active,
                )
                new_plan.save()

            return offer_update


class OfferUpdate(OfferBase):
    objects = OfferUpdateManager()
    for_offer = models.OneToOneField(Offer)
    user = models.ForeignKey(User)
    ready = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


def offer_update_published(sender, instance, raw, **kwargs):
    if instance.pk is not None:
        if instance.status == Offer.PUBLISHED:
            old_instance = Offer.objects.get(pk=instance.pk)
            if old_instance.status == Offer.UNPUBLISHED:
                instance.published_at = timezone.now()


def clean_offer_on_save(sender, instance, raw, **kwargs):
    instance.content = clean(instance.content)


pre_save.connect(clean_offer_on_save, sender=Offer)
pre_save.connect(clean_offer_on_save, sender=OfferUpdate)

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
    location = models.ForeignKey(Location)

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
    plan = models.OneToOneField(Plan, blank=True, null=True, on_delete=models.SET_NULL)


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
    reply_to = models.ForeignKey('self', blank=True, null=True)

    content = models.TextField()
    status = models.CharField(max_length=1, choices=STATE_CHOICES, default=PUBLISHED)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def is_reply(self):
        if self.reply_to is None:
            return False
        else:
            if self.reply_to.status == Comment.PUBLISHED:
                return True
            return False

    def json_data(self):
        return json.dumps({
            "content": self.content,
            "commenter": self.commenter.username,
            "comment_id": self.pk,
        })


def clean_comment_on_save(sender, instance, raw, **kwargs):
    instance.content = super_clean(instance.content)

pre_save.connect(clean_comment_on_save, sender=Comment)
