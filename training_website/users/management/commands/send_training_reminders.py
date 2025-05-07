from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from users.models import Training
from datetime import timedelta

class Command(BaseCommand):
    help = 'Отправляет напоминания участникам тренировок за 1 час до начала'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        hour_later = now + timedelta(hours=8)

        trainings = Training.objects.filter(date__range=(hour_later - timedelta(minutes=2.5), hour_later + timedelta(minutes=2.5)))

        for training in trainings:
            subject = f'Напоминание: тренировка "{training.sport_type}" скоро начнётся'
            message = f'Привет! Напоминаем, что тренировка по "{training.sport_type}" начнётся в {training.date.strftime("%H:%M %d.%m.%Y")} по адресу: {training.location}.'
            for user in training.participants.all():
                if user.email:
                    print('jnjsvns')
                    send_mail(subject, message, None, [user.email])
                    self.stdout.write(f"📩 Отправлено: {user.email}")
                self.stdout.write(f"📩BEdi")
