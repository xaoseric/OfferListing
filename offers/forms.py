from django import forms
from offers.models import Comment, Offer, Plan, Provider, OfferUpdate, PlanUpdate, Location, TestIP, TestDownload
from django.forms.models import formset_factory, modelformset_factory, inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Fieldset, HTML


class ProviderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProviderForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.add_input(Submit('save', 'Save Profile'))

    class Meta:
        model = Provider
        fields = ('name', 'start_date', 'website', 'tos', 'logo')


class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea())
    reply_to = forms.IntegerField(widget=forms.HiddenInput(), initial=-1)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.add_input(Submit('submit', 'Comment!'))


# Plans and offers

class OfferForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(OfferForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    class Meta:
        model = Offer
        fields = ('name', 'content')

PLAN_FIELDS = (
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
    'location',
)

PlanFormsetBase = inlineformset_factory(
    Offer,
    Plan,
    extra=4,
    fields=PLAN_FIELDS,
    can_delete=True,
)


class PlanFormset(PlanFormsetBase):
    def __init__(self, *args, **kwargs):
        provider = kwargs['provider']
        del kwargs["provider"]
        super(PlanFormset, self).__init__(*args, **kwargs)

        for form in self:
            form.fields["location"].queryset = Location.objects.filter(provider=provider)


PlanFormsetHelper = FormHelper()
PlanFormsetHelper.form_tag = False
PlanFormsetHelper.layout = Layout(
    Fieldset(
        'Plan specifications',
        'bandwidth',
        'disk_space',
        'memory',
        'virtualization',
        'location',
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
        'DELETE',
    ),
    'id',
)


# Offer update

class OfferUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(OfferUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    class Meta:
        model = OfferUpdate
        fields = ('name', 'content')


PlanUpdateFormsetBase = inlineformset_factory(
    OfferUpdate,
    PlanUpdate,
    extra=4,
    fields=PLAN_FIELDS,
)


class PlanUpdateFormset(PlanUpdateFormsetBase):
    def __init__(self, *args, **kwargs):
        provider = kwargs['provider']
        del kwargs["provider"]
        super(PlanUpdateFormset, self).__init__(*args, **kwargs)

        for form in self:
            form.fields["location"].queryset = Location.objects.filter(provider=provider)


# Locations
class LocationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    class Meta:
        model = Location
        fields = ('city', 'country', 'datacenter')


TestIPFormsetBase = inlineformset_factory(Location, TestIP, extra=4, fields=('ip', 'ip_type'), fk_name='location')
TestDownloadFormsetBase = inlineformset_factory(
    Location,
    TestDownload,
    extra=4,
    fields=('url', 'size'),
    fk_name='location',
)


class TestIPFormset(TestIPFormsetBase):

    def __init__(self, *args, **kwargs):
        super(TestIPFormset, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.template = 'offers/better_table_inline_form.html'
        self.helper.form_tag = False


class TestDownloadFormset(TestDownloadFormsetBase):

    def __init__(self, *args, **kwargs):
        super(TestDownloadFormset, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.template = 'offers/better_table_inline_form.html'
        self.helper.form_tag = False

        for form in self:
            form.fields["size"].label = 'Size (MB)'
