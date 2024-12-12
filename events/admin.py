from django.contrib import admin
from .models import Event, EventRegistration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin interface for managing events.
    """
    list_display = ('title', 'date', 'location', 'organizer')
    search_fields = ('title', 'location', 'organizer__username')
    list_filter = ('date', 'location')


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    """
    Admin interface for managing event registrations.
    """
    list_display = ('event', 'user', 'registered_at')
    search_fields = ('event__title', 'user__username')
    list_filter = ('registered_at',)
