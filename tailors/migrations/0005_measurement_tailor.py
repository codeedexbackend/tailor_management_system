# Generated by Django 5.0.1 on 2024-02-16 04:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tailors', '0004_rename_hips_measurement_arm_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='measurement',
            name='tailor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tailors.tailor'),
        ),
    ]
