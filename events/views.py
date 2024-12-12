from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Event, EventRegistration
from .serializers import EventSerializer, EventRegistrationSerializer
from .permissions import IsOrganizerOrReadOnly


class EventListCreateView(generics.ListCreateAPIView):
    """
    View for listing all events and creating a new event.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """
        Automatically assign the currently logged-in user as the organizer.
        """
        serializer.save(organizer=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, and deleting a specific event.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsOrganizerOrReadOnly]

    def perform_update(self, serializer):
        """
        Restricts updates to the organizer of the event.
        """
        event = self.get_object()
        if event.organizer != self.request.user:
            raise PermissionDenied("You are not allowed to update this event.")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Restricts deletion to the organizer of the event.
        """
        if instance.organizer != self.request.user:
            raise PermissionDenied("You are not allowed to delete this event.")
        instance.delete()


class EventRegistrationView(APIView):
    """
    API view for user registration for an event.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        """
        Allows a user to register for a specific event.
        """
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

        # Prevent organizer from registering for their own event
        if event.organizer == request.user:
            return Response(
                {"error": "You cannot register for your own event."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the user is already registered
        if EventRegistration.objects.filter(event=event, user=request.user).exists():
            return Response(
                {"error": "You are already registered for this event."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a new registration
        EventRegistration.objects.create(event=event, user=request.user)
        return Response({"message": "Registration successful."}, status=status.HTTP_201_CREATED)

class RegisteredUsersView(APIView):
    """
    API view for retrieving all users registered for a specific event.
    Accessible only to the event organizer.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        """
        Returns the list of registered users for the event.
        """
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the current user is the organizer
        if event.organizer != request.user:
            return Response(
                {"error": "You are not authorized to view registrations for this event."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get all registrations for the event
        registrations = EventRegistration.objects.filter(event=event)
        serializer = EventRegistrationSerializer(registrations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserRegisteredEventsView(APIView):
    """
    API view for retrieving all events a user is registered for.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Returns the list of events the user is registered for.
        """
        registrations = EventRegistration.objects.filter(user=request.user)
        serializer = EventRegistrationSerializer(registrations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
