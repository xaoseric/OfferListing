from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from offers.models import Offer, Comment, Provider
from offers.forms import CommentForm
from offers.decorators import user_is_provider
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required


def view_offer(request, offer_pk):
    offer = get_object_or_404(Offer, status=Offer.PUBLISHED, pk=offer_pk)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated():
                Comment(
                    commenter=request.user,
                    offer=offer,
                    content=form.cleaned_data["comment"],
                    status=Comment.PUBLISHED
                ).save()
                messages.success(request, "Thank you for commenting!")
                form = CommentForm()
            else:
                messages.error(request, 'You need to be logged in to comment!')
        else:
            messages.error(request, "Your comment had errors. Please fix them and submit again!")
    else:
        form = CommentForm()

    return render(request, 'offers/view.html', {
        "offer": offer,
        "form": form,
    })


def list_offers(request, page_number=1):
    offer_list = Offer.visible_offers.all()
    paginator = Paginator(offer_list, 5)

    try:
        offers = paginator.page(page_number)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        offers = paginator.page(paginator.num_pages)

    return render(request, 'offers/list.html', {"offers": offers})


def provider_list(request):
    providers = Provider.objects.order_by('name')

    return render(request, 'offers/providers.html', {
        "providers": providers
    })


def provider_profile(request, provider_pk, page_number=1):
    provider = get_object_or_404(Provider, pk=provider_pk)
    offer_list = Offer.visible_offers.for_provider(provider)

    paginator = Paginator(offer_list, 5)
    try:
        offers = paginator.page(page_number)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        offers = paginator.page(paginator.num_pages)

    return render(request, "offers/provider.html", {
        "provider": provider,
        "offers": offers,
    })


@user_is_provider
@login_required
def admin_provider_home(request):
    return HttpResponse("provider admin page")
