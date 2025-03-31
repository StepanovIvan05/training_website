from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import Training

User = get_user_model()

# Форма регистрации
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

# Форма входа
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

class TrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        fields = ['sport_type', 'date', 'location', 'description', 'image', 'max_participants']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }