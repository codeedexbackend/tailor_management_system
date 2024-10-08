# Generated by Django 3.2.10 on 2024-04-08 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0034_add_order_pending_or_delivered'),
    ]

    operations = [
        migrations.RenameField(
            model_name='add_order',
            old_name='collar',
            new_name='collar_measurements',
        ),
        migrations.RenameField(
            model_name='add_order',
            old_name='collar_size',
            new_name='cuff_measurements',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='collar',
            new_name='collar_measurements',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='collar_size',
            new_name='cuff_measurements',
        ),
        migrations.RemoveField(
            model_name='add_order',
            name='cuff_length',
        ),
        migrations.RemoveField(
            model_name='add_order',
            name='cuff_type',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cuff_length',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cuff_type',
        ),
        migrations.AddField(
            model_name='add_order',
            name='collar_type_image_url',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='add_order',
            name='cuff_type_image_url',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='collar_type_image_url',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='cuff_type_image_url',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
