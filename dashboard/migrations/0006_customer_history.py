# Generated by Django 5.0.1 on 2024-02-22 05:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_alter_addtailors_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='history',
            field=models.TextField(blank=True, null=True),
        ),
    ]
