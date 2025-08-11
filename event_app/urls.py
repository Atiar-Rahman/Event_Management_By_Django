from django.urls import path
from .views import (
    home, signup,
    EventListView, EventDetailView,
    EventCreateView, EventUpdateView, event_delete,
    CategoryListView, CategoryCreateView, category_update, category_delete,
    DashboardView, DashboardStatsView,
    rsvp_event, my_rsvped_events, cancel_rsvp,
    no_permission, dashboard_redirect
)

app_name = 'event_app'

urlpatterns = [
    path('', EventListView.as_view(), name='event_list'),
    path('home/', home, name='home'),

    path('signup/', signup, name='signup'),

    path('events/<int:id>/', EventDetailView.as_view(), name='event_detail'),
    path('events/create/', EventCreateView.as_view(), name='event_create'),
    path('events/<int:id>/edit/', EventUpdateView.as_view(), name='event_update'),
    path('events/<int:id>/delete/', event_delete, name='event_delete'),

    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:id>/edit/', category_update, name='category_update'),
    path('categories/<int:id>/delete/', category_delete, name='category_delete'),

    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard_stats_api'),

    path('rsvp/<int:event_id>/', rsvp_event, name='rsvp_event'),
    path('my-events/', my_rsvped_events, name='my_rsvped_events'),
    path('rsvp/<int:event_id>/cancel/', cancel_rsvp, name='cancel_rsvp'),

    path('no-permission/', no_permission, name='no-permission'),
    path('where-to/', dashboard_redirect, name='dashboard_redirect'),
]
