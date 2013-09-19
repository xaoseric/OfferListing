from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from accounts.forms import UserEditForm
from django.contrib import messages


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
