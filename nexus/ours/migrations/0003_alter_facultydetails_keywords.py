# Generated by Django 5.0.1 on 2024-04-03 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ours', '0002_alter_facultydetails_keywords_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facultydetails',
            name='keywords',
            field=models.ManyToManyField(blank=True, to='ours.keyword'),
        ),
    ]
