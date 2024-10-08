# Generated by Django 3.2.10 on 2024-03-11 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0029_auto_20240311_0444'),
    ]

    operations = [
        migrations.RenameField(
            model_name='add_order',
            old_name='neck_round',
            new_name='cuff_size',
        ),
        migrations.RenameField(
            model_name='add_order',
            old_name='wrist',
            new_name='seat',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='neck_round',
            new_name='cuff_size',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='wrist',
            new_name='seat',
        ),
        migrations.RemoveField(
            model_name='add_order',
            name='bottom2',
        ),
        migrations.RemoveField(
            model_name='add_order',
            name='cuff_length',
        ),
        migrations.RemoveField(
            model_name='add_order',
            name='history',
        ),
        migrations.RemoveField(
            model_name='add_order',
            name='sleeve_length',
        ),
        migrations.RemoveField(
            model_name='add_order',
            name='sleeve_type',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='bottom2',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cuff_length',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='history',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='sleeve_length',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='sleeve_type',
        ),
        migrations.AddField(
            model_name='add_order',
            name='sleeve_cuff',
            field=models.FloatField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='add_order',
            name='sleeve_sada',
            field=models.FloatField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='sleeve_cuff',
            field=models.FloatField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='sleeve_sada',
            field=models.FloatField(max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='add_order',
            name='cuff_type',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='add_order',
            name='delivery_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='customer',
            name='cuff_type',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
