from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOrganizerOrReadOnly(BasePermission):
    """
    Custom permission to allow only the organizer to edit or delete the event.
    """
    def has_object_permission(self, request, view, obj):
        # Allow read-only permissions for all users
        if request.method in SAFE_METHODS:
            return True
        # Only the organizer can modify or delete the object
        return obj.organizer == request.user
