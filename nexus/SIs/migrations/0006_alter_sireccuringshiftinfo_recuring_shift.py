# Generated by Django 5.0.1 on 2024-08-30 15:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SIs', '0005_alter_sireccuringshiftinfo_role'),
        ('shifts', '0007_remove_shift_changed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sireccuringshiftinfo',
            name='recuring_shift',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shifts.recurringshift'),
        ),
    ]
