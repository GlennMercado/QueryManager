# Generated by Django 5.1.4 on 2025-02-21 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_question_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='mark_solution',
            field=models.BooleanField(default=False),
        ),
    ]
