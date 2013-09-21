from django import forms
from offers.models import Comment, Offer, Plan
from django.forms.models import formset_factory, modelformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Fieldset, HTML


class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.add_input(Submit('submit', 'Comment!'))


class OfferForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(OfferForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    class Meta:
        model = Offer
        fields = ('name', 'content')


PlanFormset = modelformset_factory(
    Plan,
    extra=4,
    fields=(
        'virtualization',
        'bandwidth',
        'disk_space',
        'memory',
        'ipv4_space',
        'ipv6_space',
        'billing_time',
        'url',
        'promo_code',
        'cost',
    )
)
PlanFormsetHelper = FormHelper()
PlanFormsetHelper.form_tag = False
PlanFormsetHelper.layout = Layout(
    Fieldset(
        'Plan specifications',
        'bandwidth',
        'disk_space',
        'memory',
        'virtualization',
    ),
    Fieldset(
        'IP Space',
        'ipv4_space',
        'ipv6_space'
    ),
    Fieldset(
        'Billing Details',
        'billing_time',
        'url',
        'promo_code',
        'cost',
    ),
)
