from django.urls import path
from . import views

app_name = 'event_app'

urlpatterns = [
    # Events
    path('', views.EventListView.as_view(), name='event_list'),
    path('events/<int:id>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:id>/edit/', views.EventUpdateView.as_view(), name='event_update'),
    path('events/<int:id>/delete/', views.event_delete, name='event_delete'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:id>/edit/', views.category_update, name='category_update'),
    path('categories/<int:id>/delete/', views.category_delete, name='category_delete'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/stats/', views.dashboard_stats_api, name='dashboard_stats_api'),

    # RSVP
    path('rsvp/<int:event_id>/', views.rsvp_event, name='rsvp'),
    path('my-events/', views.my_rsvped_events, name='my_rsvped_events'),
    path('rsvp/<int:event_id>/cancel/', views.cancel_rsvp, name='cancel_rsvp'),

    # Permission
    path('no-permission/', views.no_permission, name='no_permission'),
]
