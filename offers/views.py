from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from offers.models import Offer, Comment, Provider, OfferRequest, Plan, OfferUpdate, Location
from offers.forms import (
    CommentForm,
    OfferForm,
    PlanFormset,
    PlanFormsetHelper,
    ProviderForm,
    PlanUpdateFormset,
    OfferUpdateForm,
    TestIPFormset,
    TestDownloadFormset,
    LocationForm,
)
from offers.decorators import user_is_provider
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging

logger = logging.getLogger(__name__)


def view_offer(request, offer_pk):
    """
    The view that displays an offer. This view is only accessible if the offer exists and the offer status
    is published. It is still possible to view an inactive offer.
    """
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
    """
    Displays a list of all visible offers. Paginated for better loading times.
    """
    offer_list = Offer.visible_offers.all()
    paginator = Paginator(offer_list, 5)

    try:
        offers = paginator.page(page_number)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        offers = paginator.page(paginator.num_pages)

    return render(request, 'offers/list.html', {"offers": offers})


def provider_list(request):
    """
    Displays a list of all providers
    """
    providers = Provider.objects.order_by('name')

    return render(request, 'offers/providers.html', {
        "providers": providers
    })


def provider_profile(request, provider_pk, page_number=1):
    """
    Displays the profile of a provider, including recent offers
    """
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
def admin_provider_home(request):
    """
    The homepage for provider users to manage their own provider
    """
    if request.method == "POST":
        form = ProviderForm(request.POST, request.FILES, instance=request.user.user_profile.provider)
        if form.is_valid():
            form.save()
            messages.success(request, "The provider's profile has been updated!")
            # Reload the form
            return HttpResponseRedirect(reverse('offer:admin_home'))
        else:
            messages.error(request, "There were errors in the updated profile. Please correct them and try again!")
    else:
        form = ProviderForm(instance=request.user.user_profile.provider)
    return render(request, 'offers/manage/home.html', {
        "provider": request.user.user_profile.provider,
        "form": form,
    })


@user_is_provider
def admin_submit_request(request):
    if request.method == "POST":

        offer = Offer(status=Offer.UNPUBLISHED, is_active=True, provider=request.user.user_profile.provider)

        form = OfferForm(request.POST, instance=offer)

        if form.is_valid():
            offer = form.save(commit=False)
            formset = PlanFormset(request.POST, instance=offer, provider=request.user.user_profile.provider)
            if formset.is_valid():
                offer.save()
                offer_request = OfferRequest(user=request.user, offer=offer)
                offer_request.save()
                formset.save()
                return HttpResponseRedirect(reverse('offer:admin_request_edit', args=[offer_request.pk]))
        else:
            formset = PlanFormset(request.POST, provider=request.user.user_profile.provider)
    else:
        form = OfferForm()
        formset = PlanFormset(queryset=Plan.objects.none(), provider=request.user.user_profile.provider)
    return render(request, 'offers/manage/new_request.html', {
        "form": form,
        "formset": formset,
        "helper": PlanFormsetHelper
    })


@user_is_provider
def admin_edit_request(request, request_pk):
    offer_request = get_object_or_404(
        OfferRequest,
        pk=request_pk,
        offer__status=Offer.UNPUBLISHED,
        offer__provider=request.user.user_profile.provider
    )
    if request.method == "POST":
        form = OfferForm(request.POST, instance=offer_request.offer)
        formset = PlanFormset(request.POST, instance=offer_request.offer, provider=request.user.user_profile.provider)
        if form.is_valid() and formset.is_valid():
            formset.save()

            # Reload form data
            form = OfferForm(instance=offer_request.offer)
            formset = PlanFormset(instance=offer_request.offer)
    else:
        form = OfferForm(instance=offer_request.offer)
        formset = PlanFormset(instance=offer_request.offer, provider=request.user.user_profile.provider)
    return render(request, 'offers/manage/edit_request.html', {
        "form": form,
        "formset": formset,
        "helper": PlanFormsetHelper,
        "offer_request": offer_request,
    })


@user_is_provider
def admin_provider_requests(request):
    requests = OfferRequest.requests.get_requests_for_provider(
        request.user.user_profile.provider
    ).order_by(
        '-created_at'
    )

    return render(request, 'offers/manage/requests.html', {"requests": requests})


@user_is_provider
def admin_provider_delete_confirm(request, request_pk):
    offer_request = get_object_or_404(
        OfferRequest,
        pk=request_pk,
        offer__status=Offer.UNPUBLISHED,
        offer__provider=request.user.user_profile.provider
    )

    if request.GET.get('delete', False):
        offer_request.offer.plan_set.all().delete()
        offer_request.offer.delete()
        messages.success(request, "The request was deleted!")
        return HttpResponseRedirect(reverse('offer:admin_requests'))

    return render(request, 'offers/manage/delete_request.html', {"offer_request": offer_request})


@user_is_provider
def admin_provider_offer_list(request):
    offers = Offer.not_requests.for_provider(request.user.user_profile.provider)

    return render(request, 'offers/manage/offer_list.html', {
        "offers": offers,
        "provider": request.user.user_profile.provider,
    })


@user_is_provider
def admin_provider_offer_edit(request, offer_pk):
    if not Offer.not_requests.filter(pk=offer_pk, provider=request.user.user_profile.provider).exists():
        return HttpResponseNotFound("Offer was not found!")
    offer = Offer.not_requests.get(pk=offer_pk)
    plans = offer.plan_set.all()

    return render(request, 'offers/manage/edit_offer.html', {
        "offer": offer,
        "plans": plans,
    })


@user_is_provider
def admin_provider_offer_mark(request, offer_pk):
    if not Offer.not_requests.filter(pk=offer_pk, provider=request.user.user_profile.provider).exists():
        return HttpResponseNotFound("Offer was not found!")
    offer = Offer.not_requests.get(pk=offer_pk)

    offer.is_active = not offer.is_active
    offer.save()

    return HttpResponseRedirect(reverse('offer:admin_offer', args=[offer.pk]))


@user_is_provider
def admin_provider_offer_plan_mark(request, offer_pk, plan_pk):
    if not Offer.not_requests.filter(pk=offer_pk, provider=request.user.user_profile.provider).exists():
        return HttpResponseNotFound("Offer was not found!")
    offer = Offer.not_requests.get(pk=offer_pk)

    if not offer.plan_set.filter(pk=plan_pk).exists():
        return HttpResponseNotFound("Plan was not found!")
    plan = offer.plan_set.get(pk=plan_pk)

    plan.is_active = not plan.is_active
    plan.save()

    return HttpResponseRedirect(reverse('offer:admin_offer', args=[offer.pk]))


@user_is_provider
def admin_provider_update_offer(request, offer_pk):
    if not Offer.not_requests.filter(pk=offer_pk, provider=request.user.user_profile.provider).exists():
        return HttpResponseNotFound("Offer was not found!")

    offer = Offer.not_requests.get(pk=offer_pk)
    offer_update = OfferUpdate.objects.get_update_for_offer(offer, request.user)

    if request.method == "POST":
        form = OfferUpdateForm(request.POST, instance=offer_update)
        formset = PlanUpdateFormset(request.POST, instance=offer_update, provider=request.user.user_profile.provider)

        if form.is_valid() and formset.is_valid():
            offer_update = form.save()
            formset.save()

            # Reload form data
            form = OfferUpdateForm(instance=offer_update)
            formset = PlanUpdateFormset(instance=offer_update, provider=request.user.user_profile.provider)
    else:
        form = OfferUpdateForm(instance=offer_update)
        formset = PlanUpdateFormset(instance=offer_update, provider=request.user.user_profile.provider)
    return render(request, 'offers/manage/update_offer.html', {
        "form": form,
        "formset": formset,
        "helper": PlanFormsetHelper,
        "offer_update": offer_update,
    })


@user_is_provider
def admin_provider_update_offer_mark(request, offer_pk):
    if not Offer.not_requests.filter(pk=offer_pk, provider=request.user.user_profile.provider).exists():
        return HttpResponseNotFound("Offer was not found!")
    offer = Offer.not_requests.get(pk=offer_pk)
    offer_update = OfferUpdate.objects.get_update_for_offer(offer, request.user)

    offer_update.ready = not offer_update.ready
    offer_update.save()

    return HttpResponseRedirect(reverse('offer:admin_offer', args=[offer.pk]))


@user_is_provider
def admin_provider_update_delete_confirm(request, offer_pk):
    if not Offer.not_requests.filter(pk=offer_pk, provider=request.user.user_profile.provider).exists():
        return HttpResponseNotFound("Offer was not found!")
    offer = Offer.not_requests.get(pk=offer_pk)
    offer_update = OfferUpdate.objects.get_update_for_offer(offer, request.user)

    if request.GET.get('delete', False):
        offer_update.planupdate_set.all().delete()
        offer_update.delete()
        messages.success(request, "The update was deleted!")
        return HttpResponseRedirect(reverse('offer:admin_offer', args=[offer.pk]))

    return render(request, 'offers/manage/update_delete_request.html', {"offer_update": offer_update})


# Provider Locations
@user_is_provider
def admin_provider_locations(request):
    locations = Location.objects.filter(provider=request.user.user_profile.provider)
    return render(request, 'offers/manage/locations.html', {"locations": locations})


@user_is_provider
def admin_provider_locations_edit(request, location_pk):
    location = get_object_or_404(Location, pk=location_pk, provider=request.user.user_profile.provider)

    if request.method == "POST":
        form = LocationForm(request.POST, instance=location)
        ip_formset = TestIPFormset(request.POST, instance=location)
        download_formset = TestDownloadFormset(request.POST, instance=location)

        if form.is_valid() and ip_formset.is_valid() and download_formset.is_valid():
            location = form.save()
            ip_formset.save()
            download_formset.save()

            # Reload form data
            form = LocationForm(instance=location)
            ip_formset = TestIPFormset(instance=location)
            download_formset = TestDownloadFormset(instance=location)
    else:
        form = LocationForm(instance=location)
        ip_formset = TestIPFormset(instance=location)
        download_formset = TestDownloadFormset(instance=location)
    return render(request, 'offers/manage/edit_location.html', {
        "form": form,
        "ip_formset": ip_formset,
        "download_formset": download_formset,
        "helper": PlanFormsetHelper,
        "location": location,
    })
