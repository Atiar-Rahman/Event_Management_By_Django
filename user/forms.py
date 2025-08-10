from django import forms
from django.contrib.auth.models import User,Permission,Group
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm


class RegisterForm(UserCreationForm):
   class Meta:
       model = User
       fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']


   def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)


       for fieldname in ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']:
           self.fields[fieldname].help_text=None
           self.fields[fieldname].widget.attrs.update({
               'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-300',
               'placeholder': self.fields[fieldname].label
           })
   def clean_email(self):
       email = self.cleaned_data.get('email')
       email_exists = User.objects.filter(email=email).exists()


       if email_exists:
           raise forms.ValidationError('Email already exists')
       return email


class LoginForm(AuthenticationForm):
   def __init__(self, request=None, *args, **kwargs):
       super().__init__(request, *args, **kwargs)


       self.fields['username'].widget.attrs.update({
           'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
           'placeholder': 'Username'
       })
       self.fields['password'].widget.attrs.update({
           'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
           'placeholder': 'Password'
       })


class AssignRoleForm(forms.Form):
    role = forms.ModelChoiceField(
        queryset = Group.objects.all(),
        empty_label='Select a Role',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Role'
    )

class CreateGroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget= forms.CheckboxSelectMultiple,
        required = False,
        label= 'Assign Permission'
    )
    class Meta:
        model = Group
        fields=['name','permissions']
        
        widgets={
            'name':forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter group name'
            })
        }