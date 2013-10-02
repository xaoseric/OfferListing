from django.contrib import admin
from offers.models import (
    Offer,
    Plan,
    Provider,
    OfferUpdate,
    PlanUpdate,
    Comment,
    Location,
    TestIP,
    TestDownload,
    Datacenter
)
from django.db.models import Q


class PlanInlineAdmin(admin.TabularInline):
    model = Plan


class OfferAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('name', 'provider', 'created_at', 'updated_at', 'status', 'is_active', 'is_request')
    list_filter = ('status', 'created_at', 'updated_at', 'is_active', 'is_request')
    filter_horizontal = ('followers',)

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


class TestIPInline(admin.TabularInline):
    model = TestIP


class TestDownloadInline(admin.TabularInline):
    model = TestDownload


class LocationAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('city', 'country', 'provider', 'datacenter')
    list_filter = ('created_at', 'updated_at')

    inlines = [
        TestIPInline,
        TestDownloadInline,
    ]


admin.site.register(Provider)
admin.site.register(Offer, OfferAdmin)
admin.site.register(OfferUpdate, OfferUpdateAdmin)
admin.site.register(Plan)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Datacenter)

# Celery
from djcelery.models import (TaskState, WorkerState,
                 PeriodicTask, IntervalSchedule, CrontabSchedule)

admin.site.unregister(TaskState)
admin.site.unregister(WorkerState)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(PeriodicTask)
