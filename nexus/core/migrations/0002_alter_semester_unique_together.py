# Generated by Django 5.0.1 on 2024-01-23 21:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='semester',
            unique_together={('term', 'year')},
        ),
    ]
