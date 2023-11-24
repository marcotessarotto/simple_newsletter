from django.contrib import admin

from core.models import Newsletter, SubscriptionToNewsletter, Message, Visitor, VisitSurvey, EventLog, EmailTemplate
from simple_newsletter.admin_utils import ExportCsvMixin, ExportRawDataCsvMixin, ExportExcelMixin
from django.utils.translation import gettext as _

# set django admin site header
admin.site.site_header = "Simple Newsletter Administration"
admin.site.site_title = "Simple Newsletter Admin Portal"
admin.site.index_title = "Welcome to Simple Newsletter Portal"


class NewsletterShortNameFilter(admin.SimpleListFilter):
    title = _('Newsletter Short Name')
    parameter_name = 'newsletter_short_name'

    def lookups(self, request, model_admin):
        # Get a list of distinct short names from CoreVisit
        short_names = Newsletter.objects.values_list('short_name', flat=True).distinct()
        return [(short_name, short_name) for short_name in short_names]

    def queryset(self, request, queryset):
        if self.value():
            # Filter RegistrationToVisit objects based on the selected short name
            return queryset.filter(newsletter__short_name=self.value())
        return queryset


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
class SubscriptionToNewsletterAdmin(admin.ModelAdmin, ExportExcelMixin):

    @admin.display(description='newsletter shortname', )
    def get_newsletter_shortname(self, obj):
        return obj.newsletter.short_name if obj.newsletter else None

    list_display = (
        'id',
        'get_newsletter_shortname',
        'subscription_confirmed',
        'verification_email_sent',
        # 'honorific',
        # 'subscribed',
        'email',
        'name',
        'surname',
        # 'is_verified',
        'created_at',
    )

    search_fields = ('id', 'email', 'name', 'surname',)
    list_filter = [NewsletterShortNameFilter]

    actions = ["export_as_excel"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin, ExportCsvMixin, ExportRawDataCsvMixin):

    @admin.display(description='newsletter shortname', )
    def get_newsletter_shortname(self, obj):
        return obj.newsletter.short_name if obj.newsletter else None

    list_display = ('id',
                    'get_newsletter_shortname',
                    'subject', 'content', 'sent', 'sent_at',
                    'created_at',
                    )
    search_fields = ('id', 'subject', 'content',)
    # list_filter = ['enabled', 'allows_subscription', ]
    actions = ["export_as_csv", "export_raw_data_as_csv"]


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name', 'last_name', 'first_name', 'job_position', 'email_address', 'nationality', 'email_sent')
    list_filter = [ 'nationality', 'email_sent']


@admin.register(VisitSurvey)
class VisitSurveyAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'ip_address', 'participated', 'met_expectations', 'interested_in_future_visits', 'participate_in_bsbf', )
    list_filter = [ 'participated', 'met_expectations', 'interested_in_future_visits', 'participate_in_bsbf']


@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'event_type', 'event_title', 'event_target', 'event_data', 'created_at')
    list_filter = [ 'event_type']


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'subject', 'created_at')
    # list_filter = [ 'name']
