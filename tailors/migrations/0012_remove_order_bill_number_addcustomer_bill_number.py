# Generated by Django 5.0.1 on 2024-02-17 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tailors', '0011_alter_order_bill_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='bill_number',
        ),
        migrations.AddField(
            model_name='addcustomer',
            name='bill_number',
            field=models.CharField(default=1, max_length=50, unique=True),
        ),
    ]
