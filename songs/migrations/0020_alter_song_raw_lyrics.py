# Generated by Django 4.1 on 2022-10-28 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0019_alter_song_audio_file_download_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='raw_lyrics',
            field=models.TextField(blank=True, null=True),
        ),
    ]
