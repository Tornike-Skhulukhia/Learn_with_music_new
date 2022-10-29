# Generated by Django 4.1 on 2022-10-27 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0003_song_audio_file_song_audio_file_download_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='song',
            name='verified',
        ),
        migrations.AddField(
            model_name='song',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='song',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
