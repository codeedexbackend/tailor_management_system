# Generated by Django 5.0.1 on 2024-02-17 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tailors', '0009_auto_20240217_1338'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='bill_number',
            field=models.CharField(default=1, max_length=50, unique=True),
        ),
    ]
