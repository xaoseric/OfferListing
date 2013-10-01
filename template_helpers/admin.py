from django.contrib.flatpages.admin import FlatPageAdmin, FlatpageForm
from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.db import models
from django import forms


class BetterFlatPageAdmin(FlatPageAdmin):

    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'class': 'ckeditor'})},
    }

    fieldsets = (
        (None, {
            'fields': ('url', 'title', 'content', 'sites')
        }),
    )

    class Media:
        js = ('ckeditor/ckeditor.js',)
        css = {
            'all': ('template_helpers/css/flatpages_css.css',),
        }


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, BetterFlatPageAdmin)