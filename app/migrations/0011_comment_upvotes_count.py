# Generated by Django 2.1.5 on 2019-03-08 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_commentvote'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='upvotes_count',
            field=models.IntegerField(default=0),
        ),
    ]
