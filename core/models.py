import uuid

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models


class Newsletter(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)
    description = models.TextField()
    from_email = models.EmailField()
    enabled = models.BooleanField(default=False)
    allows_subscription = models.BooleanField(default=True)

    privacy_policy = RichTextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.short_name})"


class SubscriptionToNewsletter(models.Model):
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE)

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

    is_verified = models.BooleanField(default=False)

    # this is used to unsubscribe and is automatically generated
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, unique=True)

    subscribed = models.BooleanField(default=True)
    unsubscribed_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"#{self.id} {self.newsletter.name} - {self.from_email} - {self.name} {self.surname} - {self.created_at}"


class Message(models.Model):
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    content = RichTextField()
    content2 = RichTextUploadingField()

    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


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

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Survey {self.id}"

    class Meta:
        verbose_name = "Visit Survey"
        verbose_name_plural = "Visit Surveys"
