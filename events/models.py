from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    """
    Represents an event such as a conference or meetup.
    """
    title = models.CharField(max_length=255, help_text="Title of the event.")
    description = models.TextField(help_text="Detailed description of the event.")
    date = models.DateTimeField(help_text="Date and time of the event.")
    location = models.CharField(max_length=255, help_text="Location of the event.")
    organizer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="organized_events",
        help_text="User who organizes the event."
    )

    def __str__(self):
        return self.title


class EventRegistration(models.Model):
    """
    Represents a user's registration for an event.
    """
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="registrations",
        help_text="The event for which the user is registering."
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="registrations",
        help_text="The user registering for the event."
    )
    registered_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp of registration.")

    class Meta:
        unique_together = ('event', 'user')  # Prevent duplicate registrations
        verbose_name = "Event Registration"
        verbose_name_plural = "Event Registrations"

    def __str__(self):
        return f"{self.user.username} registered for {self.event.title}"
