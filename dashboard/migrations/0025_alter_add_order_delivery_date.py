# Generated by Django 3.2.10 on 2024-03-04 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0024_add_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='add_order',
            name='delivery_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
