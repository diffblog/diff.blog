# Generated by Django 2.1.5 on 2019-03-08 17:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_post_score'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Comment')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.UserProfile')),
            ],
        ),
    ]
