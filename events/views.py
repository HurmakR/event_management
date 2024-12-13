from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Event, EventRegistration
from .serializers import EventSerializer, EventRegistrationSerializer
from .permissions import IsOrganizerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .filters import EventFilter
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema, extend_schema_view
from .notifications import send_registration_email


@extend_schema_view(
    get=extend_schema(
        summary="List all events",
        description="Retrieve a list of all events with optional filters and search."
    ),
    post=extend_schema(
        summary="Create a new event",
        description="Create a new event. Requires authentication."
    )
)
class EventListCreateView(generics.ListCreateAPIView):
    """
    View for listing all events and creating a new event.
    Supports advanced filtering and searching.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Applying filters
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = EventFilter  # Custom filter class
    search_fields = ['title']  # Searching by title

    def perform_create(self, serializer):
        """
        Automatically assign the currently logged-in user as the organizer.
        """
        serializer.save(organizer=self.request.user)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve event details",
        description="Retrieve detailed information about a specific event."
    ),
    put=extend_schema(
        summary="Update an event",
        description="Update the details of an event. Only the organizer can perform this action."
    ),
    delete=extend_schema(
        summary="Delete an event",
        description="Delete a specific event. Only the organizer can perform this action."
    )
)
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


@extend_schema(
    summary="Register for an event",
    description=(
        "Allows an authenticated user to register for a specific event. "
        "Returns an error if the event does not exist, the user is already registered, "
        "or if the user is the organizer of the event."
    ),
    responses={
        201: {"message": "Registration successful."},
        400: {"error": "You are already registered for this event."},
        404: {"error": "Event not found."},
    }
)
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
        # Send email confirmation
        send_registration_email(event, request.user)

        return Response({"message": "Registration successful."}, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="List registered users for an event",
    description=(
        "Returns a list of users registered for a specific event. "
        "Only accessible to the organizer of the event. "
        "Returns an error if the event does not exist or the user is not the organizer."
    ),
    responses={
        200: EventRegistrationSerializer(many=True),
        403: {"error": "You are not authorized to view registrations for this event."},
        404: {"error": "Event not found."},
    }
)
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


@extend_schema(
    summary="List events a user is registered for",
    description=(
        "Returns a list of events the authenticated user is registered for. "
        "Requires the user to be logged in."
    ),
    responses={200: EventRegistrationSerializer(many=True)},
)
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


@extend_schema(
    summary="List events by an organizer",
    description=(
        "Returns a list of events created by a specific organizer. "
        "Accessible to any user. Requires the username of the organizer."
    ),
    parameters=[
        {
            "name": "username",
            "required": True,
            "in": "path",
            "description": "The username of the organizer.",
        }
    ],
    responses={
        200: EventSerializer(many=True),
        404: {"error": "Organizer not found."},
    }
)
class EventsByOrganizerView(APIView):
    """
    API view to retrieve all events created by a specific organizer.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, username):
        """
        Returns a list of events organized by the specified user.
        """
        # Searching for organizer by username
        try:
            organizer = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "Organizer not found."}, status=status.HTTP_404_NOT_FOUND)

        # Fetching events registered to organizer
        events = Event.objects.filter(organizer=organizer)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
