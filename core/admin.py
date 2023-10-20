from django.contrib import admin

from core.models import Newsletter, SubscriptionToNewsletter
from simple_newsletter.admin_utils import ExportCsvMixin, ExportRawDataCsvMixin


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin, ExportCsvMixin, ExportRawDataCsvMixin):
    list_display = ('id', 'short_name', 'name', 'from_email', 'enabled',
                    'allows_subscription',
                    'created_at',
                    )
    search_fields = ('id', 'short_name', 'name',)
    list_filter = ['enabled', 'allows_subscription', ]
    actions = ["export_as_csv", "export_raw_data_as_csv"]


@admin.register(SubscriptionToNewsletter)
class SubscriptionToNewsletterAdmin(admin.ModelAdmin, ExportCsvMixin, ExportRawDataCsvMixin):

    @admin.display(description='newsletter shortname', )
    def get_newsletter_shortname(self, obj):
        return obj.newsletter.short_name if obj.newsletter else None

    list_display = (
        'id',
        'get_newsletter_shortname',
        'honorific',
        'email',
        'name',
        'surname',
        'is_verified',
        'created_at',
    )

    search_fields = ('id', 'email', 'name', 'surname',)
    list_filter = ['is_verified', ]

    actions = ["export_as_excel"]