# Generated by Django 4.1 on 2022-10-27 20:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('songs', '0009_alter_song_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='song',
            name='youtube_url',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.AddConstraint(
            model_name='song',
            constraint=models.UniqueConstraint(fields=('created_by', 'youtube_id'), name='unique_song_from_youtube_per_user'),
        ),
    ]
