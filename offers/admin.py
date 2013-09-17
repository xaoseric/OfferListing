from django.contrib import admin
from offers.models import Offer, Plan, Provider


class PlanInlineAdmin(admin.TabularInline):
    model = Plan


class OfferAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('name', 'provider', 'created_at', 'updated_at', 'status')
    list_filter = ('status', 'created_at', 'updated_at')

    inlines = [
        PlanInlineAdmin,
    ]

admin.site.register(Provider)
admin.site.register(Offer, OfferAdmin)
admin.site.register(Plan)