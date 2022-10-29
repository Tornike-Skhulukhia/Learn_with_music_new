# Generated by Django 4.1 on 2022-10-27 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0005_alter_song_audio_file_download_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='audio_file_download_status',
            field=models.CharField(blank=True, choices=[('0', 'Initial'), ('1', 'In progress'), ('2', 'Downloaded successfully'), ('-1', 'Failed')], max_length=2, null=True),
        ),
    ]
