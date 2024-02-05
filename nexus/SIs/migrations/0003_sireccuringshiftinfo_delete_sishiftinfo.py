# Generated by Django 5.0.1 on 2024-01-31 08:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SIs', '0002_alter_siroleinfo_assigned_class'),
        ('core', '0007_alter_classtimes_start_time'),
        ('shifts', '0003_alter_recurringshift_document_alter_shift_document'),
    ]

    operations = [
        migrations.CreateModel(
            name='SIReccuringShiftInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_time', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='core.classtimes')),
                ('recuring_shift', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='shifts.recurringshift')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='SIs.siroleinfo')),
            ],
            options={
                'unique_together': {('role', 'class_time')},
            },
        ),
        migrations.DeleteModel(
            name='SIShiftInfo',
        ),
    ]
