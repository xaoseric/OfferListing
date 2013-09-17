from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from offers.models import Offer, Comment
from offers.forms import CommentForm
from django.contrib import messages


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