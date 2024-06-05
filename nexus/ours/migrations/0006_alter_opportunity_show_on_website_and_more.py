# Generated by Django 5.0.1 on 2024-05-22 13:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ours', '0005_alter_opportunity_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opportunity',
            name='show_on_website',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='opportunity',
            name='show_on_website_end_date',
            field=models.DateField(default=datetime.date(2099, 12, 31)),
        ),
        migrations.AlterField(
            model_name='opportunity',
            name='show_on_website_start_date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]