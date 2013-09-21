from django import forms
from offers.models import Comment, Offer, Plan
from django.forms.models import formset_factory

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


class PlanForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PlanForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
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

    class Meta:
        model = Plan
        fields = (
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

PlanFormset = formset_factory(PlanForm, extra=4)
