# Generated by Django 4.1 on 2022-10-28 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0013_alter_song_audio_file_download_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='youtube_video_metadata',
            field=models.JSONField(default={}),
        ),
    ]
