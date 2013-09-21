from django import forms
from offers.models import Comment, Offer

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.add_input(Submit('submit', 'Comment!'))


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
