from rest_framework import serializers
from .models import Event, EventRegistration


class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for the Event model.
    """
    organizer = serializers.ReadOnlyField(source='organizer.username')

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'location', 'organizer']


class EventRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for the EventRegistration model.
    """
    user = serializers.ReadOnlyField(source='user.username')
    event = serializers.ReadOnlyField(source='event.title')

    class Meta:
        model = EventRegistration
        fields = ['id', 'event', 'user', 'registered_at']
