# Generated by Django 2.1.5 on 2021-06-06 17:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jobs", "0008_auto_20210606_1012"),
    ]

    operations = [
        migrations.AlterField(
            model_name="location",
            name="slug",
            field=models.SlugField(max_length=200, null=True, unique=True),
        ),
    ]
