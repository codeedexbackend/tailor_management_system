# Generated by Django 5.0.1 on 2024-02-17 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tailors', '0021_alter_addcustomer_cuf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addcustomer',
            name='bill_number',
            field=models.CharField(default='', editable=False, max_length=50, unique=True),
        ),
    ]
