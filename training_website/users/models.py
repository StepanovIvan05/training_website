from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)

class Training(models.Model):
    sport_type = models.CharField(max_length=100, verbose_name="Вид спорта")  # Вид спорта
    date = models.DateTimeField(verbose_name="Дата и время")  # Дата и время тренировки
    location = models.CharField(max_length=255, verbose_name="Место")  # Место проведения
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Организатор")  # Организатор (связь с моделью User)

    def __str__(self):
        return f"{self.sport_type} at {self.location} on {self.date}"

    class Meta:
        verbose_name = "Тренировка"
        verbose_name_plural = "Тренировки"