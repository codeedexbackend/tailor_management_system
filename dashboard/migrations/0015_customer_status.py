# Generated by Django 5.0.1 on 2024-02-24 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0014_alter_addtailors_password_alter_addtailors_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='status',
            field=models.CharField(choices=[('assigned', 'Assigned'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='assigned', max_length=20),
        ),
    ]
