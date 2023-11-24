from django.test import TestCase

# Create your tests here.
import pytest
from django.core.exceptions import ValidationError
from core.models import EmailTemplate, Newsletter, SubscriptionToNewsletter, Message, Visitor, VisitSurvey, EventLog, \
    NewsletterDeliveryRecord
from django.utils import timezone


# EmailTemplate Tests
@pytest.mark.parametrize("name, subject, body, expected_str", [
    ("Welcome", "Welcome to our service!", "Hello, welcome to our service, we're glad to have you.", "Welcome"),
    (
    "Reminder", "Your subscription is ending", "This is a reminder that your subscription is ending soon.", "Reminder"),
    ("ThankYou", "Thank you for your support!", "We appreciate your support, thank you!", "ThankYou"),
], ids=["happy-path-welcome-email", "happy-path-reminder-email", "happy-path-thankyou-email"])
def test_email_template_str(db, name, subject, body, expected_str):
    # Arrange
    email_template = EmailTemplate(name=name, subject=subject, body=body)

    # Act
    email_template.save()

    # Assert
    assert str(email_template) == expected_str


# Newsletter Tests
@pytest.mark.parametrize("name, short_name, from_email, expected_str", [
    ("Monthly News", "Monthly", "news@example.com", "Monthly News (Monthly)"),
    ("Weekly Update", "Weekly", "update@example.com", "Weekly Update (Weekly)"),
    ("Daily Digest", "Daily", "digest@example.com", "Daily Digest (Daily)"),
], ids=["happy-path-monthly-newsletter", "happy-path-weekly-update", "happy-path-daily-digest"])
def test_newsletter_str(db, name, short_name, from_email, expected_str):
    # Arrange
    newsletter = Newsletter(name=name, short_name=short_name, from_email=from_email)

    # Act
    newsletter.save()

    # Assert
    assert str(newsletter) == expected_str


# SubscriptionToNewsletter Tests
@pytest.mark.parametrize("email, name, surname, expected_str", [
    ("john.doe@example.com", "John", "Doe", "#1 Newsletter - John Doe - "),
    ("jane.smith@example.com", "Jane", "Smith", "#2 Newsletter - Jane Smith - "),
], ids=["happy-path-john-subscription", "happy-path-jane-subscription"])
def test_subscription_to_newsletter_str(db, email, name, surname, expected_str):
    # Arrange
    newsletter = Newsletter.objects.create(name="Newsletter", short_name="NL", from_email="newsletter@example.com")
    subscription = SubscriptionToNewsletter(newsletter=newsletter, email=email, name=name, surname=surname)

    # Act
    subscription.save()

    # Assert
    assert expected_str in str(subscription)


# Message Tests
@pytest.mark.parametrize("subject, content, content2, expected_str", [
    ("Announcement", "We have an announcement to make.", "<p>We have an announcement to make.</p>", "Announcement"),
    ("Update", "Here's the latest update.", "<p>Here's the latest update.</p>", "Update"),
], ids=["happy-path-announcement-message", "happy-path-update-message"])
def test_message_str(db, subject, content, content2, expected_str):
    # Arrange
    newsletter = Newsletter.objects.create(name="Newsletter", short_name="NL", from_email="newsletter@example.com")
    message = Message(newsletter=newsletter, subject=subject, content=content, content2=content2)

    # Act
    message.save()

    # Assert
    assert str(message) == expected_str


# Visitor Tests
@pytest.mark.parametrize("first_name, last_name, expected_str", [
    ("John", "Doe", "John Doe"),
    ("Jane", "Smith", "Jane Smith"),
], ids=["happy-path-visitor-john", "happy-path-visitor-jane"])
def test_visitor_str(db, first_name, last_name, expected_str):
    # Arrange
    visitor = Visitor(first_name=first_name, last_name=last_name)

    # Act
    visitor.save()

    # Assert
    assert str(visitor) == expected_str


# VisitSurvey Tests
@pytest.mark.parametrize("participated, met_expectations, expected_str", [
    (True, True, "Survey 1"),
    (False, False, "Survey 2"),
], ids=["happy-path-survey-participated", "happy-path-survey-not-participated"])
def test_visit_survey_str(db, participated, met_expectations, expected_str):
    # Arrange
    survey = VisitSurvey(participated=participated, met_expectations=met_expectations)

    # Act
    survey.save()

    # Assert
    assert str(survey) == expected_str


# EventLog Tests
@pytest.mark.parametrize("event_type, event_title, expected_str", [
    (EventLog.EMAIL_SENT, "Email Sent", "EventLog #1  event_type=EMAIL_SENT event_target=None event_title=Email Sent "),
    (EventLog.NEWSLETTER_SUBSCRIPTION_CONFIRMED, "Subscription Confirmed",
     "EventLog #2  event_type=NEWSLETTER_SUBSCRIPTION_CONFIRMED event_target=None event_title=Subscription Confirmed "),
], ids=["happy-path-event-email-sent", "happy-path-event-subscription-confirmed"])
def test_event_log_str(db, event_type, event_title, expected_str):
    # Arrange
    event_log = EventLog(event_type=event_type, event_title=event_title)

    # Act
    event_log.save()

    # Assert
    assert expected_str in str(event_log)


# NewsletterDeliveryRecord Tests
@pytest.mark.parametrize("sent_at", [
    (timezone.now()),
    (timezone.now()),
], ids=["happy-path-delivery-record-now", "happy-path-delivery-record-now-2"])
def test_newsletter_delivery_record_str(db, sent_at):
    # Arrange
    newsletter = Newsletter.objects.create(name="Newsletter", short_name="NL", from_email="newsletter@example.com")
    message = Message.objects.create(newsletter=newsletter, subject="Subject", content="Content",
                                     content2="<p>Content</p>")
    subscription = SubscriptionToNewsletter.objects.create(newsletter=newsletter, email="subscriber@example.com",
                                                           name="Subscriber", surname="Name")
    delivery_record = NewsletterDeliveryRecord(message=message, subscriber=subscription)

    # Act
    delivery_record.save()

    # Assert
    assert f"Message {message.id} sent to {subscription.email}" in str(delivery_record)
