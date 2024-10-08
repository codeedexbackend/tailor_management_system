# Generated by Django 5.0.1 on 2024-02-17 06:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tailors', '0005_measurement_tailor'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddCustomer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=15)),
                ('length', models.DecimalField(decimal_places=2, max_digits=5)),
                ('shoulder', models.DecimalField(decimal_places=2, max_digits=5)),
                ('loose', models.DecimalField(decimal_places=2, max_digits=5)),
                ('neck', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('regal', models.DecimalField(decimal_places=2, max_digits=5)),
                ('cuf', models.DecimalField(decimal_places=2, max_digits=5)),
                ('sleeve', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tailors.customer')),
                ('tailor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tailors.tailor')),
            ],
        ),
        migrations.DeleteModel(
            name='Measurement',
        ),
    ]
