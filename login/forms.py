from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Make email field required

    class Meta:
        model = User  # Use the custom User model
        fields = ['username', 'email', 'password1', 'password2']  # Include these fields
