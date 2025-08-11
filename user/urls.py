from django.urls import path
from .views import ProfileView, ProfileUpdateView, CustomPasswordChangeView

app_name = 'user'

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('password/change/', CustomPasswordChangeView.as_view(), name='password_change'),
]
