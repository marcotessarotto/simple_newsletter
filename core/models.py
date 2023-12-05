import uuid

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.utils import timezone


class EmailTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class EmailSettings(models.Model):
    name = models.CharField(max_length=100, unique=True)
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=587)  # typical values: 587, 465, 25
    use_tls = models.BooleanField(default=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)

    def to_dict(self):
        """
        Returns a dictionary representation of the model instance.
        """
        return {
            'host': self.host,
            'port': self.port,
            'use_tls': self.use_tls,
            'username': self.username,
            'password': self.password
        }

    def __str__(self):
        return f"EmailSettings for {self.host}"


class Newsletter(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)
    survey_title = models.CharField(max_length=255)

    base_url = models.CharField(max_length=255, default="https://www.replace-this-with-your-domain.com/")

    description = models.TextField()
    from_email = models.EmailField()
    # if enabled, the newsletter will be sent to all subscribers; if disabled, the newsletter will not be sent
    enabled = models.BooleanField(default=False)
    # allow users to subscribe to this newsletter through the website
    allows_subscription = models.BooleanField(default=True)

    privacy_policy = RichTextField(null=True, blank=True)

    signature = RichTextField(null=True, blank=True)

    template = models.ForeignKey(EmailTemplate, on_delete=models.PROTECT, null=True, blank=True, related_name="newsletter_template", verbose_name="Template to use to send the email newsletter")

    email_settings = models.ForeignKey(EmailSettings, on_delete=models.PROTECT, null=True, blank=True, related_name="newsletter_email_settings", verbose_name="Email settings to use to send the email newsletter")

    template_for_web_view = models.ForeignKey(EmailTemplate, on_delete=models.PROTECT, null=True, blank=True, related_name="newsletter_template_for_web_view", verbose_name="Template to use to display the email newsletter in the browser")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.short_name})"


class SubscriptionToNewsletter(models.Model):
    """A subscription by a user to a newsletter."""

    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE)
    # newsletter is used to create sending address (see SendNewsletter command),
    # so some characters are not allowed (i.e. '[`, ']' )

    BOOLEAN_CHOICES = [(False, 'No'), (True, 'Yes')]

    # https://en.wikipedia.org/wiki/English_honorifics

    # HONORIFICS = [('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Ms', 'Ms'), ('Dr', 'Dr'), ('Prof', 'Prof')]
    HONORIFICS = [('', ''), ('Mr', 'Mr'), ('Mrs', 'Mrs'), ]

    honorific = models.CharField(max_length=20,
                                 choices=HONORIFICS,
                                 verbose_name='Title',
                                 blank=True,
                                 default="")

    email = models.EmailField(max_length=200)

    name = models.CharField(max_length=200, verbose_name='Name')
    surname = models.CharField(max_length=200, verbose_name='Surname')
    nationality = models.CharField(max_length=200, verbose_name='nationality')
    company = models.CharField(max_length=200, verbose_name='Company')
    # company_vat = models.CharField(max_length=20, verbose_name='Company VAT', blank=True, null=True)
    role = models.CharField(max_length=200, verbose_name='Role')
    telephone = models.CharField(max_length=20, verbose_name='Telephone number')

    ip_address = models.GenericIPAddressField()

    notes = models.TextField(blank=True, null=True, verbose_name="Notes for the administrator")

    subscription_source = models.CharField(max_length=200, verbose_name='Subscription source', blank=True, null=True, default="visit")

    privacy_policy_accepted = models.BooleanField(blank=False,
                                                  choices=BOOLEAN_CHOICES,
                                                  verbose_name="Do you accept the Privacy Policy?")

    # this is used to confirm the subscription and is automatically generated
    subscribe_token = models.UUIDField(default=uuid.uuid4, unique=True)

    # this is used to unsubscribe and is automatically generated
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, unique=True)

    # if subscribed is False, the user has unsubscribed; see also can_send_email() below
    subscribed = models.BooleanField(default=True, verbose_name="is the user subscribed?")
    unsubscribed_at = models.DateTimeField(blank=True, null=True)

    # if and when the verification email is sent
    verification_email_sent = models.BooleanField(default=False)
    verification_email_sent_at = models.DateTimeField(blank=True, null=True)

    # if and when the subscription is confirmed (the user clicks on the link in the verification email)
    subscription_confirmed = models.BooleanField(default=False)
    subscription_confirmed_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"#{self.id} {self.newsletter.name} - {self.name} {self.surname} - {self.created_at}"

    def unsubscribe(self, additional_notes=None):
        self.subscribed = False
        self.unsubscribed_at = timezone.now()
        self.save()

        from core.business_logic import create_event_log

        create_event_log(
            event_type="UNSUBSCRIBED",
            event_title=f"User unsubscribed from newsletter {self.newsletter.short_name} - {self.newsletter.name}",
            event_data=f"Subscription: {self.id} - {self.email} additional_notes: {additional_notes}",
            event_target=self.email
        )

    def can_send_email(self):
        """
        Can we send email to this subscriber?
        Returns True if the user has subscribed to newsletter and confirmed the subscription, False otherwise.
        """
        return self.subscribed and self.subscription_confirmed


class Message(models.Model):
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, verbose_name="email subject")

    message_content = RichTextUploadingField()

    view_token = models.UUIDField(default=uuid.uuid4)

    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(blank=True, null=True)

    to_be_processed_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    web_view_counter = models.IntegerField(default=0)

    def __str__(self):
        return self.subject

    def increment_web_view_counter(self):
        self.web_view_counter += 1
        self.save()


class Visitor(models.Model):
    id = models.AutoField(primary_key=True)
    company_name = models.CharField("Name of the Company", max_length=255)
    last_name = models.CharField("Last Name", max_length=100)
    first_name = models.CharField("First Name", max_length=100)
    job_position = models.CharField("Job Position", max_length=100)
    nationality = models.CharField(max_length=100, blank=True)
    mobile_phone = models.CharField("Mobile Phone", max_length=40, blank=True, null=True)
    email_address = models.EmailField("Email Address", max_length=255)

    subscribe_token = models.UUIDField(default=uuid.uuid4, unique=True)

    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, blank=True, null=True)

    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Visitor"
        verbose_name_plural = "Visitors"


class VisitSurvey(models.Model):
    # Assuming there is a related Visitor model, you can uncomment the following line
    # visitor = models.ForeignKey('Visitor', on_delete=models.CASCADE)

    participated = models.BooleanField("Did you participate in the visit?", default=False)
    met_expectations = models.BooleanField("Did it meet your expectations?", default=False)
    aspects_made_impression = models.TextField("What are the main aspects of the visit that made an impression on you?",
                                               blank=True)
    suggestions_for_improvement = models.TextField(
        "What suggestions do you have to improve future visits to big science organizations?", blank=True)
    interested_in_future_visits = models.BooleanField(
        "Are you interested in participating in future visits to big science organizations?", default=False)
    participate_in_bsbf = models.BooleanField("Will you participate in the BSBF 2024 in Trieste?", default=False)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Survey {self.id}"

    class Meta:
        verbose_name = "Visit Survey"
        verbose_name_plural = "Visit Surveys"


class EventLog(models.Model):

    EMAIL_SENT = "EMAIL_SENT"
    NEWSLETTER_SUBSCRIPTION_CONFIRMED = "NEWSLETTER_SUBSCRIPTION_CONFIRMED"
    CONFIRM_SUBSCRIPTION_EMAIL_SENT = "CONFIRM_SUBSCRIPTION_EMAIL_SENT"
    UNSUBSCRIBED = "UNSUBSCRIBED"

    created_at = models.DateTimeField(auto_now_add=True)

    event_type = models.CharField(max_length=128, null=True)
    event_title = models.CharField(max_length=256, null=True)
    event_data = models.TextField(null=True)
    event_target = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return f"EventLog #{self.id}  event_type={self.event_type} event_target={self.event_target} event_title={self.event_title} {self.created_at}"


class NewsletterDeliveryRecord(models.Model):
    message = models.ForeignKey('Message', on_delete=models.CASCADE)
    subscriber = models.ForeignKey('SubscriptionToNewsletter', on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.message.id} sent to {self.subscriber.email} on {self.sent_at}"
