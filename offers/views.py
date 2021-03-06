from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from offers.models import Offer, Comment, Provider, Plan, Location, Datacenter, Like
from django.db.models import Q
from offers.forms import (
    CommentForm,
    OfferForm,
    PlanFormset,
    PlanFormsetHelper,
    ProviderForm,
    TestIPFormset,
    TestDownloadFormset,
    LocationForm,
)
from offers.emailers import send_comment_reply, send_comment_new, send_comment_liked, send_comment_unliked
from offers.decorators import user_is_provider
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging
from django_countries import countries as COUNTRIES
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import reversion
from django.template.loader import render_to_string
import json

logger = logging.getLogger(__name__)


def view_offer(request, offer_pk, slug=None):
    """
    The view that displays an offer. This view is only accessible if the offer exists and the offer status
    is published. It is still possible to view an inactive offer.
    """
    offer = get_object_or_404(Offer.visible_offers, pk=offer_pk)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated():
                if form.cleaned_data["reply_to"] != -1:
                    if Comment.objects.filter(pk=form.cleaned_data["reply_to"], offer=offer).exists():
                        reply_to = Comment.objects.get(pk=form.cleaned_data["reply_to"])
                    else:
                        reply_to = None
                else:
                    reply_to = None
                comment = Comment(
                    commenter=request.user,
                    offer=offer,
                    bbcode_content=form.cleaned_data["comment"],
                    status=Comment.PUBLISHED,
                    reply_to=reply_to,
                )
                comment.save()
                if comment.is_reply():
                    send_comment_reply(comment)
                send_comment_new(comment, request.user)
                messages.success(request, "Thank you for commenting!")
                form = CommentForm()
            else:
                messages.error(request, 'You need to be logged in to comment!')
        else:
            messages.error(request, "Your comment had errors. Please fix them and submit again!")
    else:
        form = CommentForm()

        if request.user.is_authenticated():
            action = request.GET.get('do', False)
            if action:
                if action == 'follow':
                    offer.followers.add(request.user)
                elif action == 'unfollow':
                    offer.followers.remove(request.user)

                return HttpResponseRedirect(offer.get_absolute_url())

    return render(request, 'offers/view.html', {
        "offer": offer,
        "form": form,
    })


@login_required
def like_comment(request, comment_pk):
    comment = get_object_or_404(Comment.visible, ~Q(commenter=request.user), pk=comment_pk)

    if comment.does_like(request.user):
        # User is trying to unlike the comment
        Like.objects.get(user=request.user, comment=comment).delete()
        send_comment_unliked(comment, request.user.username)
        does_like = False
    else:
        # User is trying to like a comment
        like = Like.objects.create(user=request.user, comment=comment)
        send_comment_liked(like)
        does_like = True

    return HttpResponse(json.dumps({
        "button": render_to_string('offers/comment_like_button.html', {"comment": comment, "is_liked": does_like}),
        "likes": render_to_string('offers/comment_like_count.html', {
            "comment_pk": comment.pk,
            "comment_likes": comment.like_count(),
            "names": comment.liked_users(),
        }),
    }), content_type='application/json')


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

    next_offer = timezone.now() + timedelta(seconds=settings.PUBLISH_SCHEDULE.is_due(timezone.now())[1])

    return render(request, 'offers/list.html', {"offers": offers, "next_offer_date": next_offer})


def provider_list(request):
    """
    Displays a list of all providers
    """
    providers = Provider.objects.order_by('name')

    return render(request, 'offers/providers.html', {
        "providers": providers
    })


def provider_profile(request, provider_name):
    """
    Displays the profile of a provider, including recent offers
    """
    provider = get_object_or_404(Provider, name_slug=provider_name)
    offer_list = Offer.visible_offers.for_provider(provider)

    paginator = Paginator(offer_list, 5)
    page = request.GET.get('page')
    try:
        offers = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        offers = paginator.page(1)
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

        offer = Offer(
            status=Offer.UNPUBLISHED,
            is_active=True,
            provider=request.user.user_profile.provider,
            creator=request.user,
            is_request=True,
        )

        form = OfferForm(request.POST, instance=offer)

        if form.is_valid():
            offer = form.save(commit=False)
            formset = PlanFormset(request.POST, instance=offer, provider=request.user.user_profile.provider)
            if formset.is_valid():
                offer.save()
                reversion.set_comment("Provider added new offer request.")
                formset.save()
                messages.success(request, 'Your offer request has been saved! You may continue to edit it below.')
                return HttpResponseRedirect(reverse('offer:admin_request_edit', args=[offer.pk]))
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
def admin_edit_request(request, offer_pk):
    offer = get_object_or_404(
        Offer.requests.for_user(request.user),
        pk=offer_pk,
    )
    if request.method == "POST":
        form = OfferForm(request.POST, instance=offer)
        formset = PlanFormset(request.POST, instance=offer, provider=request.user.user_profile.provider)
        if form.is_valid() and formset.is_valid():
            form.save()
            reversion.set_comment("Provider updated their request.")
            formset.save()

            messages.success(request, "Your offer request has been updated! You may continue to edit it below.")

            # Reload form data
            form = OfferForm(instance=offer)
            formset = PlanFormset(instance=offer, provider=request.user.user_profile.provider)
    else:
        form = OfferForm(instance=offer)
        formset = PlanFormset(instance=offer, provider=request.user.user_profile.provider)
    return render(request, 'offers/manage/edit_request.html', {
        "form": form,
        "formset": formset,
        "helper": PlanFormsetHelper,
        "offer": offer,
    })


@user_is_provider
def admin_provider_requests(request):
    requests = Offer.requests.for_user(request.user).order_by(
        '-created_at'
    )

    return render(request, 'offers/manage/requests.html', {"requests": requests})


@user_is_provider
def admin_mark_request(request, offer_pk):
    offer = get_object_or_404(
        Offer.requests.for_user(request.user),
        pk=offer_pk,
    )

    offer.is_ready = not offer.is_ready
    offer.save()

    if offer.is_ready:
        messages.success(request, "Marked offer as ready for publishing.")
        reversion.set_comment("Provider marked the request as ready.")
    else:
        messages.success(request, "Marked offer as not ready for publishing.")
        reversion.set_comment("Provider marked the request as not ready.")

    return HttpResponseRedirect(reverse('offer:admin_requests'))


@user_is_provider
def admin_provider_delete_confirm(request, offer_pk):
    offer = get_object_or_404(
        Offer.requests.for_user(request.user),
        pk=offer_pk,
    )

    if request.GET.get('delete', False):
        offer.plan_set.all().delete()
        offer.delete()
        messages.success(request, "The request was deleted!")
        return HttpResponseRedirect(reverse('offer:admin_requests'))

    return render(request, 'offers/manage/delete_request.html', {"offer": offer})


@user_is_provider
def admin_provider_offer_list(request):
    offers = Offer.not_requests.for_provider(request.user.user_profile.provider)

    return render(request, 'offers/manage/offer_list.html', {
        "offers": offers,
        "provider": request.user.user_profile.provider,
    })


@user_is_provider
def admin_provider_offer_edit(request, offer_pk):
    offer = get_object_or_404(Offer.not_requests.for_user(request.user), pk=offer_pk)
    plans = offer.plan_set.all()

    return render(request, 'offers/manage/edit_offer.html', {
        "offer": offer,
        "plans": plans,
    })


@user_is_provider
def admin_provider_offer_mark(request, offer_pk):
    offer = get_object_or_404(Offer.not_requests.for_user(request.user), pk=offer_pk)

    offer.is_active = not offer.is_active
    offer.save()

    return HttpResponseRedirect(reverse('offer:admin_offer', args=[offer.pk]))


@user_is_provider
def admin_provider_offer_plan_mark(request, offer_pk, plan_pk):
    offer = get_object_or_404(Offer.not_requests.for_user(request.user), pk=offer_pk)
    plan = get_object_or_404(offer.plan_set.all(), pk=plan_pk)

    plan.is_active = not plan.is_active
    plan.save()

    return HttpResponseRedirect(reverse('offer:admin_offer', args=[offer.pk]))


@user_is_provider
def admin_provider_update_offer(request, offer_pk):
    offer = get_object_or_404(
        Offer.not_requests.for_user(request.user),
        pk=offer_pk,
    )
    if request.method == "POST":
        form = OfferForm(request.POST, instance=offer)
        formset = PlanFormset(request.POST, instance=offer, provider=request.user.user_profile.provider)
        if form.is_valid() and formset.is_valid():
            form.save()
            reversion.set_comment("Provider updated their offer.")
            formset.save()

            messages.success(request, "Your offer has been updated! You may continue to edit it below.")

            # Reload form data
            form = OfferForm(instance=offer)
            formset = PlanFormset(instance=offer, provider=request.user.user_profile.provider)
    else:
        form = OfferForm(instance=offer)
        formset = PlanFormset(instance=offer, provider=request.user.user_profile.provider)
    return render(request, 'offers/manage/update_offer.html', {
        "form": form,
        "formset": formset,
        "helper": PlanFormsetHelper,
        "offer": offer,
    })


@user_is_provider
def admin_preview_request(request, offer_pk):
    offer = get_object_or_404(
        Offer.requests.for_user(request.user),
        pk=offer_pk
    )

    return render(request, 'offers/manage/preview.html', {
        "offer": offer
    })


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

            messages.success(request, "Your location has been updated!")

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


@user_is_provider
def admin_provider_locations_new(request):
    location = Location(provider=request.user.user_profile.provider)
    if request.method == "POST":
        form = LocationForm(request.POST, instance=location)
        ip_formset = TestIPFormset(request.POST, instance=location)
        download_formset = TestDownloadFormset(request.POST, instance=location)

        if form.is_valid() and ip_formset.is_valid() and download_formset.is_valid():
            location = form.save()
            ip_formset.save()
            download_formset.save()

            messages.success(request, "Your new location has been saved! You may continue to edit it below.")

            return HttpResponseRedirect(reverse('offer:admin_location_edit', args=[location.pk]))
    else:
        form = LocationForm(instance=location)
        ip_formset = TestIPFormset(instance=location)
        download_formset = TestDownloadFormset(instance=location)
    return render(request, 'offers/manage/new_location.html', {
        "form": form,
        "ip_formset": ip_formset,
        "download_formset": download_formset,
        "location": location,
    })


def plan_finder(request):

    country_codes = Location.objects.values_list('country').distinct()
    countries = []
    country_list = dict(COUNTRIES)
    for country_code in country_codes:
        country_code = country_code[0]
        countries.append((country_code, country_list[country_code]))


    providers = Provider.objects.all()
    datacenters = Datacenter.objects.all()

    billing_times = Plan.BILLING_CHOICES

    server_types = []

    for key, name in Plan.SERVER_CHOICES:
        if type(name) == tuple:
            for key2, name2 in name:
                server_types.append((key2, name2))
        else:
            server_types.append((key, name))

    return render(request, 'offers/plan_finder.html', {
        "countries": countries,
        "providers": providers,
        "datacenters": datacenters,
        "billing_times": billing_times,
        "server_types": server_types,
    })
