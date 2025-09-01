from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager

from core.models import (
    Semester,
)

class NexusUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if not first_name:
            raise ValueError("Users must have a first name")
        if not last_name:
            raise ValueError("Users must have a last name")
        
        user = self.model(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            **extra_fields
        )
        
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(
            email = self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
        
        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

class NexusUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True, blank=False, null=False)
    first_name = models.CharField(max_length=100, blank=False, null=False)
    last_name = models.CharField(max_length=100, blank=False, null=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = NexusUserManager()
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    class Meta(AbstractUser.Meta):
        ordering = ['last_name', 'first_name', 'email']
    
    def is_ours_mentor(self):
        return Positions.objects.filter(user=self, semester=Semester.objects.get_active_semester(), position=PositionChoices.OURS_MENTOR).exists()
    
    def is_oa(self):
        return Positions.objects.filter(user=self, semester=Semester.objects.get_active_semester(), position=PositionChoices.OFFICE_ASSISTANT).exists()

class PositionChoices(models.IntegerChoices):
    TECH = 0, 'Tech'
    SI = 1, 'SI'
    TUTOR = 2, 'Tutor'
    SI_PM = 3, 'SI PM'
    TUTOR_PM = 4, 'Tutor PM'
    GROUP_TUTOR = 5, 'Group Tutor'
    OURS_MENTOR = 6, 'OURS Mentor'
    OFFICE_ASSISTANT = 7, 'Office Assistant'
    OFFICE_ASSISTANT_PM = 8, 'Office Assistant PM'
    OURS_MENTOR_PM = 9, 'OURS Mentor PM'
    GRADUATE_TUTOR = 10, 'Graduate Tutor'
    

class Positions(models.Model):
    semester = models.ForeignKey(
        to=Semester, 
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
        help_text='The semester position is for.',
    )
    
    user = models.ForeignKey(
        to=NexusUser, 
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
        help_text='User position is for.',
    )
    
    position = models.PositiveSmallIntegerField(
        choices=PositionChoices.choices,
        null=False,
        blank=False,
        help_text='The position the user has.',
    )
    
    hourly_pay = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text='Hourly pay for the position.',
    )
    
    class Meta:
        ordering = ['semester', 'user__last_name', 'user__first_name', 'user__email', 'position']
        unique_together = ['semester', 'user', 'position']
    
    def __str__(self):
        return f"{self.user} - {self.get_position_display()} - {self.semester}"

class PositionGroups(models.Model):
    semester = models.ForeignKey(
        to=Semester, 
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text='The semester group is for.',
    )
    
    name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        help_text='Name of the group.',
    )
    
    members = models.ManyToManyField(
        to=Positions,
        related_name='groups',
        help_text='Members of the group.',
    )
    
    class Meta:
        ordering = ['semester', 'name']
        unique_together = ['semester', 'name']
    
    def __str__(self):
        return self.name