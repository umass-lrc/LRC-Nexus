from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager

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
            first_name = first_name.title(),
            last_name = last_name.title(),
            **extra_fields
        )
        
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(
            email = self.normalize_email(email),
            first_name=first_name.title(),
            last_name=last_name.title(),
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