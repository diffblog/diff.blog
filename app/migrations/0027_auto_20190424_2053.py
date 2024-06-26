# Generated by Django 2.1.5 on 2019-04-24 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_post_summary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='bio',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='company',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='github_token',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='location',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
