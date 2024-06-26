# Generated by Django 2.1.5 on 2021-06-26 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0071_auto_20210626_0644'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='posted_from',
            field=models.CharField(default='diffblog', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='blogsuggestion',
            name='status',
            field=models.IntegerField(choices=[(0, 'Pending'), (2, 'No feed'), (1, 'No GitHub account'), (3, 'Should be added by the user'), (4, 'Non English blog'), (10, 'Blog added')], default=0),
        ),
    ]
