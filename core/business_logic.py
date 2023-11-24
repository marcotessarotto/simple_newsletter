from django.utils import timezone
from .models import EventLog


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
