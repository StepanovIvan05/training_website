from django.db import models
from django.contrib.auth.models import AbstractUser
from django import forms
from django.utils import timezone

class User(AbstractUser):
    email = models.EmailField(unique=True)

class Training(models.Model):
    sport_type = models.CharField(max_length=100, verbose_name="Вид спорта")
    date = models.DateTimeField(verbose_name="Дата и время")
    location = models.CharField(max_length=255, verbose_name="Место")
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Организатор")

    def clean(self):
        if self.date < timezone.now():
            raise forms.ValidationError("Дата не может быть в прошлом!")

    def __str__(self):
        return f"{self.sport_type} - {self.date}"
