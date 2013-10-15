from offers.models import Offer
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.feedgenerator import Atom1Feed


class OfferFeed(Feed):
    title = settings.SITE_NAME + ' offers'
    description = 'A recent list of offers on ' + settings.SITE_NAME
    description_template = 'offers/generic/offer_release.html'
    item_guid_is_permalink = True

    def items(self):
        return Offer.visible_offers.all()

    def link(self):
        return reverse('home')

    def item_author_name(self, item):
        return item.provider.name

    def item_pubdate(self, item):
        return item.published_at


class OfferAtomFeed(OfferFeed):
    feed_type = Atom1Feed
    subtitle = OfferFeed.description
