from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import Permission, Group

User = get_user_model()


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make email required at the form level
        if 'email' in self.fields:
            self.fields['email'].required = True

        for fieldname in ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']:
            if fieldname in self.fields:
                self.fields[fieldname].help_text = None
                self.fields[fieldname].widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-300',
                    'placeholder': self.fields[fieldname].label
                })

        # Nice to have: autofocus on username
        if 'username' in self.fields:
            self.fields['username'].widget.attrs['autofocus'] = True

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        if not email:
            return email

        # Case-insensitive uniqueness check; ignore instance if editing in future
        qs = User.objects.all()
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.filter(email__iexact=email).exists():
            raise forms.ValidationError('Email already exists')
        return email


class LoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        if 'username' in self.fields:
            self.fields['username'].widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Username'
            })
        if 'password' in self.fields:
            self.fields['password'].widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Password'
            })


class AssignRoleForm(forms.Form):
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label='Select a Role',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Role'
    )


class CreateGroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple(),  # <-- instantiate the widget
        required=False,
        label='Assign Permissions'
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter group name'
            })
        }
