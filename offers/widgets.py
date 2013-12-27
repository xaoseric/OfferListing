from django import forms


class MarkdownTextField(forms.Textarea):
    def render(self, name, value, attrs=None):
        html = super(MarkdownTextField, self).render(name, value, attrs)
        return html + "Custom markdown field"
