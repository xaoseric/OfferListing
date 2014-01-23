from haystack import indexes
from offers.models import Offer


class OfferIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    provider = indexes.CharField(model_attr='provider')

    status = indexes.CharField(model_attr='status')

    published_at = indexes.DateTimeField(model_attr='published_at')
    content_auto = indexes.EdgeNgramField(use_template=True, template_name='search/indexes/offers/offer_text.txt')

    def get_model(self):
        return Offer

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().visible_offers.all()