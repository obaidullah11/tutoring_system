# adminpanel/models.py

from django.db import models
from django.conf import settings

class ClassRoom(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'Admin'}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='courses')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_type': 'Admin'}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
