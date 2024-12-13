from django.core.mail import send_mail
from django.conf import settings


def send_registration_email(event, user):
    """
    Sends an email confirmation to the user after successful registration.
    """
    subject = f"Registration Confirmation for {event.title}"
    message = (
        f"Dear {user.username},\n\n"
        f"You have successfully registered for the event '{event.title}'.\n"
        f"Details:\n"
        f"Date: {event.date}\n"
        f"Location: {event.location}\n\n"
        f"Thank you for registering!\n\n"
        f"Best regards,\n"
        f"Event Management Team"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
