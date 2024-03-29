# Generated by Django 2.1.5 on 2021-03-08 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0051_auto_20210307_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogsuggestion',
            name='status',
            field=models.IntegerField(choices=[(10, 'Blog added'), (3, 'Should be added by the user'), (2, 'No feed'), (4, 'Non English blog'), (1, 'No GitHub account'), (0, 'Pending')], default=0),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='github_username',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
