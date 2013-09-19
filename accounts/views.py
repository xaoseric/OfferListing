from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.urlresolvers import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            messages.success(request, 'You have been logged in!')
            if form.cleaned_data["next"]:
                return HttpResponseRedirect(form.cleaned_data["next"])
            else:
                return reverse('home')
        else:
            messages.error(request, "There was a problem logging you in")
    else:
        form = AuthenticationForm(request.GET)
    helper = FormHelper()
    helper.add_input(Submit('login', 'Login'))
    form.helper = helper
    return render(request, 'accounts/login.html', {"form": form})
