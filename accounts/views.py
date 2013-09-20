from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate
from django.shortcuts import render
from accounts.forms import UserEditForm, UserConfirmDeletionForm
from django.contrib import messages
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth import logout as logout_user
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from offers.models import Comment


@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {"user": request.user})


@login_required
def edit_account(request):
    if request.method == "POST":
        form = UserEditForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data["first_name"]
            request.user.last_name = form.cleaned_data["last_name"]
            request.user.email = form.cleaned_data["email"]
            request.user.save()
            messages.success(request, 'You account has been successfully updated!')
        else:
            messages.error(request, 'The form had errors. Please correct them and submit again.')
    else:
        form = UserEditForm({
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
        })
    return render(request, 'accounts/edit.html', {"form": form})


@login_required
def change_password(request):
    helper = FormHelper()
    helper.add_input(Submit('save', 'Change Password'))

    if request.method == "POST":
        form = PasswordChangeForm(
            request.user,
            request.POST
        )
        if form.is_valid():
            messages.success(request, "You password has been changed!")
            form.save()
    else:
        form = PasswordChangeForm(request.user)

    form.helper = helper
    return render(request, 'accounts/change_password.html', {"form": form})


@login_required
def deactivate_account(request):
    if request.method == "POST":
        form = UserConfirmDeletionForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
            if user is None or user != request.user:
                messages.error(request, "Invalid username or password!")
            else:
                request.user.is_active = False
                request.user.save()
                logout_user(request)
                messages.success(
                    request,
                    "Your account has been deactivated! Please contact a staff member to reactivate your account!"
                )
                return HttpResponseRedirect(reverse("home"))
    else:
        form = UserConfirmDeletionForm()
    return render(request, 'accounts/deactivate.html', {"form": form})


@login_required
def comment_list(request):
    comments = Comment.objects.filter(commenter=request.user)
    return render(request, 'accounts/comments.html', {"comments": comments})
