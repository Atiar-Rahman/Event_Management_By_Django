from django import forms
from .models import Event, Category, Participant
from django.core.exceptions import ValidationError

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','description']

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['name','email']

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name','description','date','time','location','category','participants']
        widgets = {
            'date': forms.DateInput(attrs={'type':'date'}),
            'time': forms.TimeInput(attrs={'type':'time'}),
            'participants': forms.SelectMultiple(),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name','').strip()
        if not name:
            raise ValidationError("Event name cannot be empty")
        return name
