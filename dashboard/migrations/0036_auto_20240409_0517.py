# Generated by Django 3.2.10 on 2024-04-09 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0035_auto_20240408_1019'),
    ]

    operations = [
        migrations.AddField(
            model_name='add_order',
            name='collar_type',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='add_order',
            name='cuff_type',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='collar_type',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='cuff_type',
            field=models.CharField(max_length=15, null=True),
        ),
    ]
