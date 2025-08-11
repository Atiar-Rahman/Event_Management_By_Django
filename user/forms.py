from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'profile_picture')
        widgets = {
            'username': forms.TextInput(attrs={'class':'w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500'}),
            'email': forms.EmailInput(attrs={'class':'w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500'}),
            'first_name': forms.TextInput(attrs={'class':'w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500'}),
            'last_name': forms.TextInput(attrs={'class':'w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500'}),
            'phone_number': forms.TextInput(attrs={'class':'w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class':'w-full text-sm text-gray-600'}),
        }

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'profile_picture')

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name','last_name','phone_number','profile_picture')
        widgets = {
            'first_name': forms.TextInput(attrs={'class':'w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500'}),
            'last_name': forms.TextInput(attrs={'class':'w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500'}),
            'phone_number': forms.TextInput(attrs={'class':'w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class':'w-full text-sm text-gray-600'}),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({'class':'w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500'})
