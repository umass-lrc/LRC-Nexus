from django.db import migrations, models

# Selectable like any other location, for opportunities spread over many places
MULTIPLE_LOCATIONS = [
    'Multiple Locations : US',
    'Multiple Locations : International',
]

def copy_location_to_locations(apps, schema_editor):
    Opportunity = apps.get_model('ours', 'Opportunity')
    Location = apps.get_model('ours', 'Location')
    for name in MULTIPLE_LOCATIONS:
        Location.objects.get_or_create(name=name)
    for opportunity in Opportunity.objects.exclude(location__isnull=True):
        name = opportunity.location.strip()
        if len(name) == 0:
            continue
        location = Location.objects.get_or_create(name=name)[0]
        opportunity.locations.add(location)


def copy_locations_to_location(apps, schema_editor):
    Opportunity = apps.get_model('ours', 'Opportunity')
    for opportunity in Opportunity.objects.all():
        names = [location.name for location in opportunity.locations.all()]
        if names:
            opportunity.location = '; '.join(names)[:255]
            opportunity.save(update_fields=['location'])


class Migration(migrations.Migration):

    dependencies = [
        ('ours', '0012_opportunity_featured'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='opportunity',
            name='locations',
            field=models.ManyToManyField(blank=True, to='ours.location'),
        ),
        migrations.RunPython(copy_location_to_locations, copy_locations_to_location),
        migrations.RemoveField(
            model_name='opportunity',
            name='location',
        ),
    ]
