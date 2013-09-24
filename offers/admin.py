from django.contrib import admin
from offers.models import Offer, Plan, Provider, OfferUpdate, PlanUpdate
from django.db.models import Q


class PlanInlineAdmin(admin.TabularInline):
    model = Plan


class ActiveRequestFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'active request'

    parameter_name = 'active_request'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('T', 'Is Request'),
            ('F', 'Is Not Request'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'T':
            return queryset.filter(Q(status=Offer.UNPUBLISHED), ~Q(request=None))
        if self.value() == 'F':
            return queryset.filter(
                Q(status=Offer.PUBLISHED) |
                (Q(request=None) & Q(status=Offer.UNPUBLISHED))
            )


class OfferAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('name', 'provider', 'created_at', 'updated_at', 'status', 'is_active', 'is_request')
    list_filter = ('status', 'created_at', 'updated_at', 'is_active', ActiveRequestFilter)

    inlines = [
        PlanInlineAdmin,
    ]

admin.site.register(Provider)
admin.site.register(Offer, OfferAdmin)
admin.site.register(OfferUpdate)
admin.site.register(PlanUpdate)
admin.site.register(Plan)