# Generated by Django 4.1 on 2022-10-27 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0010_song_created_by_song_youtube_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='published_at',
            field=models.DateField(blank=True, null=True),
        ),
    ]
