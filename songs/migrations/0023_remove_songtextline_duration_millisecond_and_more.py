# Generated by Django 4.1 on 2022-10-29 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('songs', '0022_alter_songtextline_duration_millisecond_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='songtextline',
            name='duration_millisecond',
        ),
        migrations.AddField(
            model_name='songtextline',
            name='end_time_millisecond',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
