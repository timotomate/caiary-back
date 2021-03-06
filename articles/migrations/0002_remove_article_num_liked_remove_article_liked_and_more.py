# Generated by Django 4.0.4 on 2022-05-21 12:50

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='num_liked',
        ),
        migrations.RemoveField(
            model_name='article',
            name='liked',
        ),
        migrations.AddField(
            model_name='article',
            name='liked',
            field=models.ManyToManyField(related_name='like_articles', to=settings.AUTH_USER_MODEL),
        ),
    ]
