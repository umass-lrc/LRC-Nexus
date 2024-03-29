# Generated by Django 5.0.1 on 2024-01-29 14:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SIs', '0001_initial'),
        ('core', '0007_alter_classtimes_start_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siroleinfo',
            name='assigned_class',
            field=models.ForeignKey(blank=True, help_text='The class that this role is for.', null=True, on_delete=django.db.models.deletion.RESTRICT, to='core.classes'),
        ),
    ]
