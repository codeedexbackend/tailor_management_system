# Generated by Django 5.0.1 on 2024-02-19 10:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tailors', '0029_rename_tailor_name_addtailor_tailorname_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='addtailor',
            old_name='tailorname',
            new_name='tailor_name',
        ),
    ]
