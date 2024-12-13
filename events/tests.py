from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from knox.models import AuthToken
from .models import Event, EventRegistration


class EventCRUDTest(APITestCase):
    def setUp(self):
        """
        Set up test data for CRUD operations.
        """
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = AuthToken.objects.create(self.user)[1]  # Generate Knox token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')  # Add token to headers
        self.event_data = {
            'title': 'Test Event',
            'description': 'Test Event Description',
            'date': '2024-12-31T10:00:00Z',
            'location': 'Test Location'
        }

    def test_create_event(self):
        """
        Test creating a new event.
        """
        response = self.client.post('/api/events/', self.event_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)

    def test_retrieve_event(self):
        """
        Test retrieving an event by ID.
        """
        event = Event.objects.create(organizer=self.user, **self.event_data)
        response = self.client.get(f'/api/events/{event.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.event_data['title'])

    def test_update_event(self):
        """
        Test updating an event.
        """
        event = Event.objects.create(organizer=self.user, **self.event_data)
        update_data = {
            'title': 'Updated Event',
            'description': 'Updated Description',
            'date': '2024-12-31T10:00:00Z',
            'location': 'Updated Location'
        }  # Include all required fields
        response = self.client.put(f'/api/events/{event.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Event.objects.get(id=event.id).title, 'Updated Event')

    def test_delete_event(self):
        """
        Test deleting an event.
        """
        event = Event.objects.create(organizer=self.user, **self.event_data)
        response = self.client.delete(f'/api/events/{event.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Event.objects.count(), 0)


class EventRegistrationTest(APITestCase):
    def setUp(self):
        """
        Set up test data for event registration.
        """
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.organizer = User.objects.create_user(username='organizer', password='organizerpass')
        self.token = AuthToken.objects.create(self.user)[1]  # Generate Knox token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')  # Add token to headers
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            date='2024-12-31T10:00:00Z',
            location='Test Location',
            organizer=self.organizer
        )

    def test_register_for_event(self):
        """
        Test registering for an event.
        """
        response = self.client.post(f'/api/events/{self.event.id}/register/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EventRegistration.objects.count(), 1)

    def test_register_twice(self):
        """
        Test that registering twice for the same event is not allowed.
        """
        self.client.post(f'/api/events/{self.event.id}/register/')
        response = self.client.post(f'/api/events/{self.event.id}/register/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_organizer_cannot_register(self):
        """
        Test that the organizer cannot register for their own event.
        """
        self.client.logout()
        self.token = AuthToken.objects.create(self.organizer)[1]  # Generate token for the organizer
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        response = self.client.post(f'/api/events/{self.event.id}/register/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserRegisteredEventsTest(APITestCase):
    def setUp(self):
        """
        Set up test data for retrieving user's registered events.
        """
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = AuthToken.objects.create(self.user)[1]  # Generate Knox token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')  # Add token to headers
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            date='2024-12-31T10:00:00Z',
            location='Test Location',
            organizer=self.user
        )
        EventRegistration.objects.create(event=self.event, user=self.user)

    def test_view_registered_events(self):
        """
        Test viewing events the user is registered for.
        """
        response = self.client.get('/api/user/registrations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['event'], self.event.title)


class RegisteredUsersTest(APITestCase):
    def setUp(self):
        """
        Set up test data for retrieving registered users.
        """
        self.organizer = User.objects.create_user(username='organizer', password='organizerpass')
        self.token = AuthToken.objects.create(self.organizer)[1]  # Generate Knox token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')  # Add token to headers
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            date='2024-12-31T10:00:00Z',
            location='Test Location',
            organizer=self.organizer
        )
        self.user1 = User.objects.create_user(username='user1', password='user1pass')
        self.user2 = User.objects.create_user(username='user2', password='user2pass')
        EventRegistration.objects.create(event=self.event, user=self.user1)
        EventRegistration.objects.create(event=self.event, user=self.user2)

    def test_view_registered_users(self):
        """
        Test viewing registered users for an event.
        """
        response = self.client.get(f'/api/events/{self.event.id}/registrations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['user'], self.user1.username)
        self.assertEqual(response.data[1]['user'], self.user2.username)
