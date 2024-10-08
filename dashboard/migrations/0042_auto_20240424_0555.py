# Generated by Django 3.2.10 on 2024-04-24 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0041_alter_admin_login_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admin_login',
            name='user',
        ),
        migrations.RemoveField(
            model_name='reception_login',
            name='user',
        ),
        migrations.AddField(
            model_name='admin_login',
            name='password',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='admin_login',
            name='username',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='reception_login',
            name='password',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='reception_login',
            name='user_name',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
