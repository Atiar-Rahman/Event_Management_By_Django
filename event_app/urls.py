from django.urls import path
from .views import (
    home, signup,
    EventListView, EventDetailView,
    EventCreateView, EventUpdateView, event_delete,
    dashboard, dashboard_stats_api,   # ← added
    rsvp_event, my_rsvped_events, cancel_rsvp,
    category_list, CategoryCreateView, category_update, category_delete,
    no_permission, dashboard_redirect
)

app_name = 'event_app'

urlpatterns = [
    path('', EventListView.as_view(), name='event_list'),
    path('home/', home, name='home'),

    # auth
    path('signup/', signup, name='signup'),

    # events
    path('events/<int:id>/', EventDetailView.as_view(), name='event_detail'),
    path('events/create/', EventCreateView.as_view(), name='event_create'),
    path('events/<int:id>/edit/', EventUpdateView.as_view(), name='event_update'),
    path('events/<int:id>/delete/', event_delete, name='event_delete'),

    # dashboards & rsvp
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard-stats/', dashboard_stats_api, name='dashboard_stats_api'),  # ← new API route
    path('rsvp/<int:event_id>/', rsvp_event, name='rsvp_event'),
    path('my-events/', my_rsvped_events, name='my_rsvped_events'),
    path('rsvp/<int:event_id>/cancel/', cancel_rsvp, name='cancel_rsvp'),

    # categories
    path('categories/', category_list, name='category_list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:id>/edit/', category_update, name='category_update'),
    path('categories/<int:id>/delete/', category_delete, name='category_delete'),

    # misc
    path('no-permission/', no_permission, name='no-permission'),
    path('where-to/', dashboard_redirect, name='dashboard_redirect'),
]
