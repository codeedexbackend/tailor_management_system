# Generated by Django 3.2.10 on 2024-05-11 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0047_auto_20240510_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='add_order',
            name='pocket_type',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='pocket_type',
            field=models.CharField(max_length=15, null=True),
        ),
    ]
