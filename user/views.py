from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages

from .models import CustomUser
from .forms import ProfileUpdateForm, CustomPasswordChangeForm

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user/profile.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['user_obj'] = self.request.user
        return ctx

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = 'user/profile_form.html'
    success_url = reverse_lazy('user:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('user:profile')

    def form_valid(self, form):
        messages.success(self.request, "Password changed successfully.")
        return super().form_valid(form)
