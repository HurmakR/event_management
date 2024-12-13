import django_filters
from .models import Event


class EventFilter(django_filters.FilterSet):
    """
    Custom filter for Event model.
    """
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte", help_text="Filter events starting from this date.")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte", help_text="Filter events ending at this date.")
    location_contains = django_filters.CharFilter(field_name="location", lookup_expr="icontains", help_text="Search events by partial location.")
    organizer = django_filters.CharFilter(field_name="organizer__username", lookup_expr="exact", help_text="Filter events by organizer username.")

    class Meta:
        model = Event
        fields = ['date_from', 'date_to', 'location_contains', 'organizer']
