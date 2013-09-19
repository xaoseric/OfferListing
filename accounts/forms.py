from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class BetterAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(BetterAuthenticationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('login', 'Login'))