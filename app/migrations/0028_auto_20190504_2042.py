# Generated by Django 2.1.5 on 2019-05-04 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0027_auto_20190424_2053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='score',
            field=models.FloatField(default=0),
        ),
    ]