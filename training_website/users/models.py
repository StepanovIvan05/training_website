from django.db import models
from django.contrib.auth.models import AbstractUser
from django import forms
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    email = models.EmailField(unique=True)
    organizer_rating = models.FloatField(default=0, verbose_name="Рейтинг организатора")
    participant_rating = models.FloatField(default=0)

    def update_organizer_rating(self):
        trainings = Training.objects.filter(organizer=self)
        trainings = [
            training for training in trainings
            if training.end_time <= timezone.now()
        ]
        reviews = Review.objects.filter(training__in=trainings)

        if reviews.exists():
            total = sum([review.rating for review in reviews])
            self.organizer_rating = total / reviews.count()
            self.save()
        else:
            self.organizer_rating = 0
            self.save()


class SportType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Training(models.Model):
    sport_type = models.ForeignKey(SportType, on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name="Дата и время")
    location = models.CharField(max_length=255, verbose_name="Место")
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Организатор")
    description = models.TextField(blank=True, verbose_name="Описание")  # Описание тренировки
    image = models.ImageField(upload_to='training_images/', blank=True, null=True, verbose_name="Фото события")  # Фото
    max_participants = models.PositiveIntegerField(default=10, verbose_name="Максимальное количество участников")  # Лимит участников
    participants = models.ManyToManyField(User, related_name="trainings", blank=True)  # Записавшиеся
    duration = models.PositiveIntegerField(verbose_name="Продолжительность (в минутах)", default=60)

    @property
    def end_time(self):
        return self.date + timedelta(minutes=self.duration-420)

    @property
    def is_finished(self):
        return timezone.now() >= self.end_time

    def is_full(self):
        return self.participants.count() >= self.max_participants

    def clean(self):
        if self.date < timezone.now():
            raise forms.ValidationError("Дата не может быть в прошлом!")

    def __str__(self):
        return f"{self.sport_type} - {self.date}"
    
class Review(models.Model):
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('training', 'author')  # один отзыв от участника на тренировку

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # обновляем рейтинг организатора
        self.training.organizer.update_organizer_rating()

    def __str__(self):
        return f"Отзыв от {self.author} на {self.training}"
    