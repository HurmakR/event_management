
# Event Management API

A Django REST API for managing events, user registrations, and notifications.

## Features
- CRUD operations for events (Create, Read, Update, Delete).
- User registration and authentication using Knox tokens.
- Event registration for users.
- Email notifications upon successful registration.
- Advanced filtering and search for events.
- API documentation with Swagger and Redoc.
- Dockerized setup for easy deployment.

---

## Installation

### Prerequisites
- Python 3.12+
- Docker and Docker Compose

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/event-management-api.git
   cd event-management-api
   ```

2. Create a `.env` file with the following environment variables:
   ```env
   # Database configuration
   DATABASE_URL=postgres://postgres:password@db:5432/event_management

   # Email settings
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_email_password
   ```

3. Build and start the Docker containers:
   ```bash
   docker-compose up --build
   ```

4. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

---

## Usage

### Endpoints

| Method | Endpoint                           | Description                           |
|--------|------------------------------------|---------------------------------------|
| `POST` | `/api/auth/register/`              | Register a new user                  |
| `POST` | `/api/auth/login/`                 | Login and obtain a token             |
| `GET`  | `/api/events/`                     | List all events                      |
| `POST` | `/api/events/`                     | Create a new event                   |
| `GET`  | `/api/events/<id>/`                | Retrieve event details               |
| `PUT`  | `/api/events/<id>/`                | Update an event                      |
| `DELETE` | `/api/events/<id>/`              | Delete an event                      |
| `POST` | `/api/events/<id>/register/`       | Register for an event                |
| `GET`  | `/api/events/<id>/registrations/`  | View registered users (organizer only) |
| `GET`  | `/api/user/registrations/`         | View events the user is registered for |
| `GET`  | `/api/events/organizer/<username>/` | View events by a specific organizer  |

---

## API Documentation

- **Swagger**: [http://localhost:8000/api/docs/swagger/](http://localhost:8000/api/docs/swagger/)
- **Redoc**: [http://localhost:8000/api/docs/redoc/](http://localhost:8000/api/docs/redoc/)

---

## Testing

Run tests with the following command:
```bash
docker-compose exec web python manage.py test
```

---

## Notifications

The API sends email notifications when a user successfully registers for an event. Update your `.env` file with your SMTP credentials for email functionality.

---

## Environment Variables

Ensure you have the following variables in your `.env` file:
```env
# Database configuration
DATABASE_URL=postgres://postgres:password@db:5432/event_management

# Email settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_password
```

---

## Deployment

To deploy the application, use the Docker Compose production configuration. Ensure you configure a secure database and email backend in a production environment.

---

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push the branch.
4. Submit a pull request.

---

