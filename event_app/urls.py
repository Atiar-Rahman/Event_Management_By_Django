from django.urls import path
from . import views

app_name = 'event_app'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/<int:pk>/update/', views.event_update, name='event_update'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),

    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    path('events/<int:pk>/rsvp/', views.rsvp_event, name='event_rsvp'),
    path('events/<int:pk>/cancel-rsvp/', views.cancel_rsvp, name='event_cancel_rsvp'),
    path('participant/dashboard/', views.participant_dashboard, name='participant_dashboard'),

    path('dashboard/', views.organizer_dashboard, name='dashboard'),
    path('dashboard/stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
]
