from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls), # Admin
    path('api/auth/', include('auth_app.urls')),  # Authentication
    path('api/', include('events.urls')),  # Events
]
