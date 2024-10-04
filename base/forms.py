from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class MyUserCreationForm(UserCreationForm):
    name = forms.CharField(max_length=100, required=True, label="Full Name")
    email = forms.EmailField(required=True, label="Email Address")
    
    class Meta:
        model = User
        fields = ["name", "username", "email", "password1", "password2"]
    
    def __init__(self, *args, **kwargs):
        super(MyUserCreationForm, self).__init__(*args, **kwargs)
        
        # Custom labels for form fields
        self.fields['username'].label = "Username"
        self.fields['username'].widget.attrs['placeholder'] = "Enter your username"

        self.fields['email'].label = "Email"
        self.fields['email'].widget.attrs['placeholder'] = "Enter your email"

        self.fields['name'].label = "Full Name"
        self.fields['name'].widget.attrs['placeholder'] = "Enter your full name"

        self.fields['password1'].label = "Password"
        self.fields['password1'].widget.attrs['placeholder'] = "Enter a secure password"

        self.fields['password2'].label = "Confirm Password"
        self.fields['password2'].widget.attrs['placeholder'] = "Re-enter the password"


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ["avatar", "name", "username", "email", "bio"]