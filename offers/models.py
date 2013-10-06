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
import bbcode
import html2text

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

    def for_user(self, user):
        return self.for_provider(user.user_profile.provider)


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


class OfferActiveManager(OfferVisibleManager):
    """
    Only gets the active offers (offers which are published and have the active status)
    """
    def get_query_set(self):
        return super(OfferActiveManager, self).get_query_set().filter(is_active=True)

    def for_provider(self, provider):
        """
        Returns all visible offers for a provider
        """
        return self.get_query_set().filter(provider=provider)


class OfferRequestManager(models.Manager):
    def get_query_set(self):
        return super(OfferRequestManager, self).get_query_set().filter(
            status=Offer.UNPUBLISHED,
            is_request=True,
        )

    def for_provider(self, provider):
        return self.get_query_set().filter(provider=provider)

    def for_user(self, user):
        return self.for_provider(user.user_profile.provider)


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


class CommentVisibleManager(models.Manager):
    def get_query_set(self):
        return super(CommentVisibleManager, self).get_query_set().filter(
            status=Comment.PUBLISHED,
            offer__status=Offer.PUBLISHED,
            offer__is_request=False,
        )


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


class Datacenter(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Location(models.Model):
    city = models.CharField(max_length=255)
    country = CountryField()
    datacenter = models.ForeignKey(Datacenter)
    looking_glass = models.URLField(max_length=255, null=True, blank=True)

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


class Offer(models.Model):
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
    not_requests = OfferNotRequestManager()
    requests = OfferRequestManager()

    is_request = models.BooleanField(default=False)

    is_ready = models.BooleanField(default=False)
    readied_at = models.DateTimeField(auto_now_add=True)

    creator = models.ForeignKey(User, null=True, blank=True)
    followers = models.ManyToManyField(User, blank=True, null=True, related_name="followed_offers")

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
        if not self.is_request or self.status == Offer.PUBLISHED or not self.is_ready:
            return None
        return Offer.requests.filter(
            readied_at__lt=self.readied_at, is_ready=True,
        ).count()+1
    queue_position.short_description = "Queue position"
    queue_position.admin_order_field = 'readied_at'

    def get_plan_locations(self):
        locations = []
        for plan in self.plan_set.all():
            if plan.location not in locations:
                locations.append(plan.location)
        return locations

    def get_min_max_cost(self):
        """
        Get the minimum and maximum values of the plans for each
        """

        billing_type_lookup = dict(Plan.BILLING_CHOICES)

        min_maxes = []

        for billing_type in self.plan_set.values('billing_time').distinct():
            billing_type = billing_type["billing_time"]

            min = self.plan_set.filter(billing_time=billing_type).aggregate(cost=models.Min('cost'))["cost"]
            max = self.plan_set.filter(billing_time=billing_type).aggregate(cost=models.Max('cost'))["cost"]

            is_same = False
            if min == max:
                is_same = True

            min_maxes.append({
                "code": billing_type,
                "name": billing_type_lookup[billing_type],
                "min": min,
                "max": max,
                "same": is_same,
            })
        return min_maxes

    class Meta:
        ordering = ['-published_at']


def offer_update_published(sender, instance, raw, **kwargs):
    if instance.pk is not None:
        if instance.status == Offer.PUBLISHED:
            old_instance = Offer.objects.get(pk=instance.pk)
            if old_instance.status == Offer.UNPUBLISHED:
                instance.published_at = timezone.now()

                if not instance.is_request:
                    from offers.tasks import publish_offer
                    publish_offer.delay(instance.pk)
        elif instance.is_ready:
            old_instance = Offer.objects.get(pk=instance.pk)
            if not old_instance.is_ready:
                # Comment became ready
                instance.readied_at = timezone.now()


def clean_offer_on_save(sender, instance, raw, **kwargs):
    instance.content = clean(instance.content)


pre_save.connect(clean_offer_on_save, sender=Offer)
pre_save.connect(offer_update_published, sender=Offer)


class Plan(models.Model):
    KVM = 'k'
    OPENVZ = 'o'
    XEN = 'x'
    VMWARE = 'v'

    DEDICATED = 'd'

    SERVER_CHOICES = (
        (DEDICATED, 'Dedicated'),
        ('Virtualized', (
            (KVM, 'KVM'),
            (OPENVZ, 'OpenVZ'),
            (XEN, 'Xen'),
            (VMWARE, 'VMware'),
        )),
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

    server_type = models.CharField(max_length=1, choices=SERVER_CHOICES, default=OPENVZ)

    # Offer
    offer = models.ForeignKey(Offer)

    # Data attributes
    bandwidth = models.BigIntegerField()  # In gigabytes
    disk_space = models.BigIntegerField()  # In gigabytes
    memory = models.BigIntegerField()  # In megabytes
    cpu_cores = models.IntegerField(default=1)
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
    bbcode_content = models.TextField()
    status = models.CharField(max_length=1, choices=STATE_CHOICES, default=PUBLISHED)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    visible = CommentVisibleManager()

    class Meta:
        ordering = ['created_at']

    def is_reply(self):
        if self.reply_to is None:
            return False
        else:
            if self.reply_to.status == Comment.PUBLISHED and self.reply_to.offer.status == Offer.PUBLISHED:
                return True
            return False

    def json_data(self):
        return json.dumps({
            "content": self.content,
            "commenter": self.commenter.username,
            "comment_id": self.pk,
        })

    def like_count(self):
        return self.like_set.count()

    def does_like(self, user):
        """
        Tests if the given user likes this comment

        :param user: The user to check
        :type user: User
        :return: Either True or False, based on if the user likes the comment
        :rtype: bool
        """

        return self.like_set.filter(user=user).exists()

    def liked_users(self):
        """
        A comma separated list of users who have liked this comment
        :return: The comma separated list of users
        :rtype: str
        """
        return ', '.join([like.user.username for like in self.like_set.all()])

    def text_comment(self):
        """
        The plaintext version of the comment
        :return: The plaintext version of the comment (in markdown syntax)
        :rtype: str
        """
        converted = html2text.HTML2Text()
        return converted.handle(self.content)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        parser = bbcode.Parser()
        parser.add_simple_formatter('code', '<pre>%(value)s</pre>')

        self.bbcode_content = self.bbcode_content.strip()
        self.content = parser.format(self.bbcode_content)

        super(Comment, self).save(force_insert, force_update, using, update_fields)


class Like(models.Model):
    user = models.ForeignKey(User)
    comment = models.ForeignKey(Comment)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('user', 'comment'),)
