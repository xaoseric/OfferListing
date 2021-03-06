from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset
from captcha.fields import CaptchaField
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

class UserResetPassRequestForm(forms.Form):
    username = forms.CharField(max_length=254)
    email = forms.EmailField(max_length=75)

    def __init__(self, *args, **kwargs):
        super(UserPassResetRequestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('initpwreset', 'Request Password Reset'))

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username__iexact=username)
        except User.DoesNotExist:
           raise forms.ValidationError(self.error_messages['username_notfound'])

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email_iexact=email)
        except User.DoesNotExist:
            raise forms.ValidationError(self.error_messages['email_notfound'])

    class Meta:
        model = User
        fields = ('username', 'email')


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


class UserRegisterForm(UserCreationForm):

    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Credentials',
                'username',
                'password1',
                'password2',
            ),
            Fieldset(
                'General Details',
                'first_name',
                'last_name',
                'email',
                'captcha',
            ),
            Submit('register', 'Register')
        )

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.save()
        return user
