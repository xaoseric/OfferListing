from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms


class BetterAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(BetterAuthenticationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('login', 'Login'))


class UserEditForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=75)

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('update', 'Update Account'))


class UserConfirmDeletionForm(forms.Form):

    username = forms.CharField(max_length=254)
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        max_length=4096,
    )

    def __init__(self, *args, **kwargs):
        super(UserConfirmDeletionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('confirm', 'Confirm Deletion'))
