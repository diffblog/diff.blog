# Generated by Django 2.1.5 on 2021-07-11 09:16

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0073_auto_20210711_0909'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='plugin_public_api_key',
            field=models.CharField(default=app.models.get_random_lowercase_string_of_50_chars, max_length=50),
        ),
    ]
