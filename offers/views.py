from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from offers.models import Offer


def offer(request, offer_pk):
    offer = get_object_or_404(Offer, status=Offer.PUBLISHED, pk=offer_pk)
    return HttpResponse("Got offer!" + offer.name)