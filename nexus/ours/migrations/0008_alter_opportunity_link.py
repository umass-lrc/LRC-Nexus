# Generated by Django 5.0.1 on 2024-06-05 01:16

import ours.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ours', '0007_opportunity_link_not_working_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opportunity',
            name='link',
            field=models.URLField(default=ours.models.url_for_page_not_found, unique=True),
        ),
    ]