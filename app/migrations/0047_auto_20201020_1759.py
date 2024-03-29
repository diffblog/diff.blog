# Generated by Django 2.1.5 on 2020-10-20 17:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0046_auto_20201018_0832'),
    ]

    operations = [
        migrations.CreateModel(
            name='Search',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query', models.CharField(max_length=100)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='searches', to='app.UserProfile')),
            ],
        ),
        migrations.AlterField(
            model_name='blogsuggestion',
            name='status',
            field=models.IntegerField(choices=[(10, 'Blog added'), (0, 'Pending'), (1, 'No GitHub account'), (2, 'No feed'), (3, 'Should be added by the user'), (4, 'Non English blog')], default=0),
        ),
    ]
