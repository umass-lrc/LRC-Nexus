# Generated by Django 5.0.1 on 2024-02-22 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SIs', '0003_sireccuringshiftinfo_delete_sishiftinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='siroleinfo',
            name='all_sections',
            field=models.BooleanField(default=False, help_text='If this role is for all sections of the class.'),
        ),
    ]