# Generated by Django 3.2.10 on 2024-02-28 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0018_alter_addtailors_mobile_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addtailors',
            name='mobile_number',
            field=models.CharField(max_length=15, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='mobile',
            field=models.CharField(max_length=15),
        ),
    ]
