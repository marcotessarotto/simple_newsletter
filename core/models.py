import uuid

from django.db import models


class Newsletter(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)
    description = models.TextField()
    from_email = models.EmailField()
    enabled = models.BooleanField(default=False)
    allows_subscription = models.BooleanField(default=True)

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
        return f"#{self.id} {self.newsletter.name} - {self.email} - {self.name} {self.surname} - {self.created_at}"
