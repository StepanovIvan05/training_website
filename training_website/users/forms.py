from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import Training, SportType

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

    sport_type = forms.ModelChoiceField(queryset=SportType.objects.all(), empty_label="Выберите вид спорта")

    class Meta:
        model = Training
        fields = ['sport_type', 'date', 'location', 'description', 'image', 'max_participants']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            }

class TrainingFilterForm(forms.Form):
    sport = forms.ModelChoiceField(
        queryset=SportType.objects.all().order_by('name'),
        required=False,
        label='Фильтр:',
    )
    organizer = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label='',
    )
    location = forms.ChoiceField(
        choices=[],
        required=False,
        label='',
    )
    date = forms.ChoiceField(
        choices=[],
        required=False,
        label='',
    )
    sort = forms.ChoiceField(
        choices=[
            ('date', 'Дате'),
            ('location', 'Месту'),
            ('organizer', 'Организатору'),
            ('sport', 'Виду спорта'),
        ],
        required=False,
        label='Сортировка по'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем только уникальные значения, которые есть в базе
        self.fields['sport'].choices = [('', 'Вид спорта')] + [
            (sprt, SportType.objects.get(id=sprt).name) for sprt in Training.objects.values_list('sport_type', flat=True).distinct()
        ]

        self.fields['organizer'].choices = [('', 'Организатор')] + [
            (org, Training.objects.get(id=org).organizer.username) for org in Training.objects.values_list('organizer', flat=True).distinct()
        ]

        self.fields['location'].choices = [('', 'Место')] + [
            (loc, loc) for loc in Training.objects.values_list('location', flat=True).distinct()
        ]
        self.fields['date'].choices = [('', 'Дата')] + [
            (dt, dt.strftime('%Y-%m-%d %H:%M')) for dt in Training.objects.values_list('date', flat=True).distinct()
        ]
