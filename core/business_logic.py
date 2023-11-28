from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .models import EventLog, SubscriptionToNewsletter, NewsletterDeliveryRecord, Message


def create_event_log(event_type, event_title, event_data, event_target=None):
    """
    Creates an instance of EventLog with the provided details.

    Args:
    event_type (str): The type of the event (e.g., EMAIL_SENT, NEWSLETTER_SUBSCRIPTION_CONFIRMED).
    event_title (str): A short title or description of the event.
    event_data (str): Additional data or details about the event.
    event_target (str, optional): The target or subject of the event. Defaults to None.

    Returns:
    EventLog: The created EventLog instance.
    """
    try:
        event_log = EventLog(
            event_type=event_type,
            event_title=event_title,
            event_data=event_data,
            event_target=event_target,
            created_at=timezone.now()
        )
        event_log.save()
        return event_log
    except Exception as e:
        print(e)
        return None


def find_subscriber_by_email_and_newsletter(email, newsletter__id):
    """
    Finds a subscriber by email and newsletter.

    Args:
    email (str): The email address of the subscriber.
    newsletter__id (Newsletter): The newsletter id.

    Returns:
    SubscriptionToNewsletter: The found subscriber or None if not found.
    """

    # notice: at the moment, multiuple subscriptions with the same email are allowed
    rs = SubscriptionToNewsletter.objects.filter(newsletter__id=newsletter__id).filter(email=email)
    return None if rs.count() == 0 else rs[0]


def has_message_been_sent_to_subscriber(email, message_id):
    """
    Checks if a message has been sent to a subscriber with the given email.

    Args:
    email (str): The email address of the subscriber.
    message_id (int): The ID of the message.

    Returns:
    bool: True if the message has been sent to the subscriber, False otherwise.
    """
    try:
        # get message instance from message_id:
        message = Message.objects.get(id=message_id)

        # get newsletter instance from message:
        newsletter = message.newsletter

        subscriber = find_subscriber_by_email_and_newsletter(email, newsletter.id)
        if subscriber is None:
            return False

        # Check if the message has been sent to this subscriber
        return NewsletterDeliveryRecord.objects.filter(
            subscriber=subscriber,
            message_id=message_id
        ).exists()
    except ObjectDoesNotExist:
        # Subscriber not found or other query issues
        return False


def register_message_delivery(message_id, subscriber_id):
    """
    Registers that a message has been sent to a subscriber.

    Args:
    message_id (int): The ID of the message.
    subscriber_id (int): The ID of the subscriber.

    Returns:
    NewsletterDeliveryRecord: The created record of the message delivery.
    """
    # Retrieve the Message and SubscriptionToNewsletter instances
    message = Message.objects.get(id=message_id)
    subscriber = SubscriptionToNewsletter.objects.get(id=subscriber_id)

    # Create a new NewsletterDeliveryRecord instance
    delivery_record = NewsletterDeliveryRecord(
        message=message,
        subscriber=subscriber,
        sent_at=timezone.now()
    )

    # Save the record to the database
    delivery_record.save()

    return delivery_record
