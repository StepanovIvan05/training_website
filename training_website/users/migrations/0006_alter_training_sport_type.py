# Generated by Django 5.1.7 on 2025-04-16 05:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_sporttype_alter_training_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='training',
            name='sport_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.sporttype'),
        ),
    ]
