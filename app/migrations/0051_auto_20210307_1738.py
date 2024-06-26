# Generated by Django 2.1.5 on 2021-03-07 17:29

from django.db import migrations, models

def update_organization_types(apps, schema_editor):
    UserProfile = apps.get_model('app', 'UserProfile')
    users = UserProfile.objects.filter(is_activated=False, is_organization=False)
    for user in users:
        user.is_organization = None
        user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0050_auto_20210307_1052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogsuggestion',
            name='status',
            field=models.IntegerField(choices=[(2, 'No feed'), (4, 'Non English blog'), (3, 'Should be added by the user'), (0, 'Pending'), (10, 'Blog added'), (1, 'No GitHub account')], default=0),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='is_organization',
            field=models.BooleanField(null=True),
        ),
        migrations.RunPython(update_organization_types),
    ]
