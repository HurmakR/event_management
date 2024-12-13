from django.urls import path
from .views import (
    EventListCreateView, EventDetailView, EventRegistrationView,
    RegisteredUsersView, UserRegisteredEventsView, EventsByOrganizerView
)

urlpatterns = [
    path('events/', EventListCreateView.as_view(), name='event-list-create'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('events/<int:pk>/register/', EventRegistrationView.as_view(), name='event-register'),
    path('events/<int:pk>/registrations/', RegisteredUsersView.as_view(), name='registered-users'),
    path('user/registrations/', UserRegisteredEventsView.as_view(), name='user-registrations'),
    path('events/organizer/<str:username>/', EventsByOrganizerView.as_view(), name='events-by-organizer'),
]
