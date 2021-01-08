from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, PasswordInput, Form
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rbac.models import UserProfile


class LoginForm(Form):
    username: CharField = CharField(label="Username")
    password = CharField(label="Password", widget=PasswordInput)

    def clean(self):
        user_name = self.cleaned_data['username']
        password_user = self.cleaned_data['password']
        user = authenticate(username=user_name, password=password_user)
        if not user:
            raise ValidationError({"username": "Incorrect password or user"})
        return user


class UserForm(ModelForm):
    password = CharField(label="Password", widget=PasswordInput)
    password2 = CharField(label="Verify Password", widget=PasswordInput)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password != password2:
            raise ValidationError({'password2': 'Password mismatch'})


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ("bio", "location", "birth_date")
