from django.urls import path
from .views import SignupView, ProfileView, ProfileUpdateView, CustomPasswordChangeView

app_name = 'user'
urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('password/change/', CustomPasswordChangeView.as_view(), name='password_change'),
]
