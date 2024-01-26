# Generated by Django 5.0.1 on 2024-01-21 23:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Buildings',
            fields=[
                ('short_name', models.CharField(help_text='The short name of the building. For example, "LIBR" for Library.', max_length=10, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(help_text='The name of the building.', max_length=50, unique=True)),
            ],
            options={
                'ordering': ['short_name'],
            },
        ),
        migrations.CreateModel(
            name='Classes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='CourseSubject',
            fields=[
                ('short_name', models.CharField(help_text='The short name of the course subject. For example, "COMPSCI" for Computer Science.', max_length=10, primary_key=True, serialize=False, unique=True)),
                ('description', models.CharField(help_text='The description of the course subject. For example, "Computer Science".', max_length=100)),
            ],
            options={
                'ordering': ['short_name'],
            },
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(help_text='The first name of the faculty.', max_length=50)),
                ('last_name', models.CharField(help_text='The last name of the faculty.', max_length=50)),
                ('email', models.EmailField(help_text='The email of the faculty.', max_length=254, unique=True)),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term', models.PositiveSmallIntegerField(choices=[(0, 'Spring'), (1, 'Summer - University'), (2, 'Summer - UWW Session 1'), (3, 'Summer - UWW Session 2'), (4, 'Fall'), (5, 'Winter')], help_text='The term of the semester')),
                ('year', models.PositiveSmallIntegerField(help_text='The year of the semester')),
                ('active', models.BooleanField(default=False, help_text='Whether or not the semester is active? There can only be one active semester at a time.')),
                ('classes_start', models.DateField(help_text='The date classes start for the semester. This information will be use to create recurring shifts for classes.')),
                ('classes_end', models.DateField(help_text='The date classes end for the semester. This information will be use to create recurring shifts for classes.')),
            ],
            options={
                'ordering': ['classes_start'],
            },
        ),
        migrations.CreateModel(
            name='ClassTimes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_day', models.PositiveSmallIntegerField(choices=[(0, 'Sunday'), (1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday')], help_text='The day of the week the class occurs on.')),
                ('time', models.TimeField(help_text='The time of the class.')),
                ('duration', models.DurationField(help_text='The duration of the class.')),
                ('room', models.CharField(help_text='The room the class occurs in.', max_length=10)),
                ('building', models.ForeignKey(help_text='The building the class occurs in.', on_delete=django.db.models.deletion.RESTRICT, to='core.buildings')),
                ('orignal_class', models.ForeignKey(help_text='The class the class time belongs to.', on_delete=django.db.models.deletion.CASCADE, to='core.classes', verbose_name='class')),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(help_text='The course number.', max_length=10)),
                ('name', models.CharField(help_text='The name of the course.', max_length=100)),
                ('is_cross_listed', models.BooleanField(default=False, help_text='Whether or not the course is cross listed. (Not true for the main course in a cross listed course.)')),
                ('main_course', models.ForeignKey(blank=True, help_text='The main course for the cross listed course.', null=True, on_delete=django.db.models.deletion.RESTRICT, to='core.course')),
                ('subject', models.ForeignKey(help_text='The department the course belongs to.', on_delete=django.db.models.deletion.RESTRICT, to='core.coursesubject')),
            ],
            options={
                'ordering': ['subject', 'number'],
            },
        ),
        migrations.AddField(
            model_name='classes',
            name='course',
            field=models.ForeignKey(help_text='The course the class belongs to.', on_delete=django.db.models.deletion.RESTRICT, to='core.course'),
        ),
        migrations.AddField(
            model_name='classes',
            name='faculty',
            field=models.ForeignKey(help_text='The faculty teaching the class.', on_delete=django.db.models.deletion.RESTRICT, to='core.faculty'),
        ),
        migrations.CreateModel(
            name='Holiday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(help_text='The date of the holiday. All shifts on this date will be cancelled.')),
                ('semester', models.ForeignKey(help_text='The semester the holiday occurs in.', on_delete=django.db.models.deletion.CASCADE, to='core.semester')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='DaySwitch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(help_text='The date of the day switch. This date will act as "day to follow" for recurring shifts.')),
                ('day_to_follow', models.PositiveSmallIntegerField(choices=[(0, 'Sunday'), (1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday')])),
                ('semester', models.ForeignKey(help_text='The semester the day switch occurs in.', on_delete=django.db.models.deletion.CASCADE, to='core.semester')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.AddField(
            model_name='classes',
            name='semester',
            field=models.ForeignKey(help_text='The semester the class occurs in.', on_delete=django.db.models.deletion.RESTRICT, to='core.semester'),
        ),
    ]