# Generated by Django 2.1.5 on 2021-06-13 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0069_auto_20210613_0624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogsuggestion',
            name='status',
            field=models.IntegerField(choices=[(10, 'Blog added'), (1, 'No GitHub account'), (2, 'No feed'), (3, 'Should be added by the user'), (0, 'Pending'), (4, 'Non English blog')], default=0),
        ),
    ]
