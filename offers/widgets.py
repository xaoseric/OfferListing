from __future__ import absolute_import, unicode_literals
from django import forms
from django.forms.util import flatatt
from django.utils.html import format_html
from django.utils.encoding import force_text


class MarkdownTextField(forms.Textarea):
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        return format_html(
            '<textarea{0}>\r\n{1}</textarea><br><div class="markdown-render"></div>',
            flatatt(final_attrs),
            force_text(value)
        )
