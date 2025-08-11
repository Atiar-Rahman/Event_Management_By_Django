from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from user.models import CustomUser
from .models import Event, Category

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username','email','first_name','last_name','phone_number','profile_picture')
        widgets = {
            'username': forms.TextInput(attrs={'class':'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500','placeholder':'Username'}),
            'email': forms.EmailInput(attrs={'class':'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500','placeholder':'Email'}),
            'first_name': forms.TextInput(attrs={'class':'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500','placeholder':'First Name'}),
            'last_name': forms.TextInput(attrs={'class':'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500','placeholder':'Last Name'}),
            'phone_number': forms.TextInput(attrs={'class':'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500','placeholder':'Phone Number'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class':'w-full text-sm text-gray-600'}),
        }

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username','email','first_name','last_name','phone_number','profile_picture')
        widgets = CustomUserCreationForm.Meta.widgets

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name','last_name','phone_number','profile_picture')
        widgets = {
            'first_name': forms.TextInput(attrs={'class':'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500','placeholder':'First Name'}),
            'last_name': forms.TextInput(attrs={'class':'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500','placeholder':'Last Name'}),
            'phone_number': forms.TextInput(attrs={'class':'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500','placeholder':'Phone Number'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class':'w-full text-sm text-gray-600'}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name','description','date','time','location','category','image']
        widgets = {
            'name': forms.TextInput(attrs={'class':'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500','placeholder':'Event Name'}),
            'description': forms.Textarea(attrs={'rows':4,'class':'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500','placeholder':'Event Description'}),
            'date': forms.DateInput(attrs={'type':'date','class':'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'time': forms.TimeInput(attrs={'type':'time','class':'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'location': forms.TextInput(attrs={'class':'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500','placeholder':'Event Location'}),
            'category': forms.Select(attrs={'class':'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'image': forms.ClearableFileInput(attrs={'class':'w-full text-sm text-gray-600'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','description']
        widgets = {
            'name': forms.TextInput(attrs={'class':'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500','placeholder':'Category Name'}),
            'description': forms.Textarea(attrs={'rows':3,'class':'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500','placeholder':'Category Description'}),
        }
