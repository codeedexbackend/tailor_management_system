# Generated by Django 5.0.1 on 2024-02-17 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tailors', '0020_rename_name_tailor_username_alter_addcustomer_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addcustomer',
            name='cuf',
            field=models.CharField(choices=[('cuff', 'Cuff'), ('normal', 'Normal')], default='normal', max_length=10),
        ),
    ]
