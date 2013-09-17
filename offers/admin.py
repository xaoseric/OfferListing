from django.contrib import admin
from offers.models import Offer, Plan, Provider


class PlanInlineAdmin(admin.TabularInline):
    model = Plan


class OfferAdmin(admin.ModelAdmin):
    inlines = [
        PlanInlineAdmin,
    ]

admin.site.register(Provider)
admin.site.register(Offer, OfferAdmin)
admin.site.register(Plan)