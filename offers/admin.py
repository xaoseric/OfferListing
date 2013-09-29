from django.contrib import admin
from offers.models import Offer, Plan, Provider, OfferUpdate, PlanUpdate, Comment
from django.db.models import Q


class PlanInlineAdmin(admin.TabularInline):
    model = Plan


class OfferAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('name', 'provider', 'created_at', 'updated_at', 'status', 'is_active', 'is_request')
    list_filter = ('status', 'created_at', 'updated_at', 'is_active', 'is_request')

    inlines = [
        PlanInlineAdmin,
    ]


class CommentAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('offer', 'commenter', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'updated_at')


class PlanUpdateInlineAdmin(admin.TabularInline):
    model = PlanUpdate


class OfferUpdateAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('name', 'provider', 'user', 'for_offer', 'created_at', 'updated_at', 'status', 'ready')
    list_filter = ('ready', 'status', 'created_at', 'updated_at')

    inlines = [
        PlanUpdateInlineAdmin,
    ]


admin.site.register(Provider)
admin.site.register(Offer, OfferAdmin)
admin.site.register(OfferUpdate, OfferUpdateAdmin)
admin.site.register(Plan)
admin.site.register(Comment, CommentAdmin)
