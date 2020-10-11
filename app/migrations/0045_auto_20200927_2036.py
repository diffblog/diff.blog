# Generated by Django 2.1.5 on 2020-09-27 20:36

from django.db import migrations, models
import random, string

def set_default_key(apps, schema_editor):
    UserProfile = apps.get_model('app', 'UserProfile')
    profiles = UserProfile.objects.all()
    for profile in profiles:
        profile.unsubscribe_key = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(50))
        profile.save()

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0044_auto_20200913_1345'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='unsubscribe_key',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.RunPython(set_default_key),
    ]