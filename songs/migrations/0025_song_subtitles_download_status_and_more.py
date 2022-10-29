# Generated by Django 4.1 on 2022-10-29 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0024_alter_language_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='subtitles_download_status',
            field=models.CharField(choices=[('0', 'Initial'), ('1', 'Processing'), ('2', 'Downloaded'), ('-1', 'Failed')], default='0', max_length=2),
        ),
        migrations.AddField(
            model_name='song',
            name='subtitles_video_youtube_id',
            field=models.CharField(max_length=11, null=True),
        ),
    ]