from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from offers.models import Offer, Comment, Provider, OfferRequest, Plan
from offers.forms import CommentForm, OfferForm, PlanFormset, PlanFormsetHelper, ProviderForm
from offers.decorators import user_is_provider
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from crispy_forms.helper import FormHelper


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
@login_required
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
@login_required
def admin_submit_request(request):
    if request.method == "POST":

        offer = Offer(status=Offer.UNPUBLISHED, is_active=True, provider=request.user.user_profile.provider)

        form = OfferForm(request.POST, instance=offer)
        formset = PlanFormset(request.POST)

        if form.is_valid() and formset.is_valid():
            offer = form.save()
            offer_request = OfferRequest(user=request.user, offer=offer)
            offer_request.save()
            for plan_form in formset:
                if plan_form.has_changed():
                    plan = plan_form.save(commit=False)
                    plan.offer = offer
                    plan.is_active = True
                    plan.save()
            return HttpResponseRedirect(reverse('offer:admin_request_edit', args=[offer_request.pk]))
    else:
        form = OfferForm()
        formset = PlanFormset(queryset=Plan.objects.none())
    return render(request, 'offers/manage/new_request.html', {
        "form": form,
        "formset": formset,
        "helper": PlanFormsetHelper
    })


@user_is_provider
@login_required
def admin_edit_request(request, request_pk):
    offer_request = get_object_or_404(
        OfferRequest,
        pk=request_pk,
        offer__status=Offer.UNPUBLISHED,
        offer__provider=request.user.user_profile.provider
    )
    if request.method == "POST":
        form = OfferForm(request.POST, instance=offer_request.offer)
        formset = PlanFormset(request.POST, queryset=Plan.objects.filter(offer=offer_request.offer))

        if form.is_valid() and formset.is_valid():
            form.save()
            for plan_form in formset:
                if plan_form.has_changed():
                    if plan_form.cleaned_data["DELETE"]:
                        continue
                    plan = plan_form.save(commit=False)
                    plan.offer = offer_request.offer
                    plan.is_active = True
                    plan.save()
            for plan_form in formset.deleted_forms:
                if plan_form.instance.pk is not None:
                    plan = plan_form.save(commit=False)
                    plan.delete()

            # Reload form data
            form = OfferForm(instance=offer_request.offer)
            formset = PlanFormset(queryset=Plan.objects.filter(offer=offer_request.offer))
    else:
        form = OfferForm(instance=offer_request.offer)
        formset = PlanFormset(queryset=Plan.objects.filter(offer=offer_request.offer))
    return render(request, 'offers/manage/edit_request.html', {
        "form": form,
        "formset": formset,
        "helper": PlanFormsetHelper,
        "offer_request": offer_request,
    })


@user_is_provider
@login_required
def admin_provider_requests(request):
    requests = OfferRequest.requests.get_requests_for_provider(
        request.user.user_profile.provider
    ).order_by(
        '-created_at'
    )

    return render(request, 'offers/manage/offers.html', {"requests": requests})


@user_is_provider
@login_required
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
