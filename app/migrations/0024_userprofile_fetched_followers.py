# Generated by Django 2.1.5 on 2019-03-25 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_userprofile_is_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='fetched_followers',
            field=models.BooleanField(default=False),
        ),
    ]
