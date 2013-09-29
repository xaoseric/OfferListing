from django import forms
from offers.models import Comment, Offer, Plan, Provider, OfferUpdate, PlanUpdate, Location, TestIP, TestDownload
from django.forms.models import formset_factory, modelformset_factory, inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Fieldset, HTML
from crispy_forms.bootstrap import AppendedText, PrependedAppendedText


class ProviderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProviderForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields["start_date"].help_text = "The date your company started."
        self.fields["tos"].help_text = \
            "A link to your terms of service that will be displayed at the bottom of each offer."
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
        self.helper.layout = Layout(
            'comment',
            'reply_to',
            Div('', css_id='comment_reply_to'),
            Submit('submit', 'Comment!')
        )


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

            form.fields["ipv4_space"].help_text = "The number of IPv4 addresses that this plan has."
            form.fields["ipv6_space"].help_text = "The number of IPv6 addresses that this plan has."
            form.fields["url"].help_text = "The url to purchase this plan."
            form.fields["promo_code"].help_text = "The optional promo code the client needs to enter to get a discount."


PlanFormsetHelper = FormHelper()
PlanFormsetHelper.form_tag = False
PlanFormsetHelper.layout = Layout(
    Fieldset(
        'Plan specifications',
        AppendedText('bandwidth', 'GB'),
        AppendedText('disk_space', 'GB'),
        AppendedText('memory', 'MB'),
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
        PrependedAppendedText('cost', '$', 'USD'),
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

            form.fields["ipv4_space"].help_text = "The number of IPv4 addresses that this plan has."
            form.fields["ipv6_space"].help_text = "The number of IPv6 addresses that this plan has."
            form.fields["url"].help_text = "The url to purchase this plan."
            form.fields["promo_code"].help_text = "The optional promo code the client needs to enter to get a discount."


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
