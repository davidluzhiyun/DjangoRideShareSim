from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Your custom fields here
    
    class Meta:
        db_table = 'rides_user'

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='rides_user_groups',
        help_text='The groups this user belongs to.'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='rides_user_permissions',
        help_text='Specific permissions for this user.'
    )