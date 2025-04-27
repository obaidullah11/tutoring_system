# adminpanel/admin.py

from django.contrib import admin
from .models import ClassRoom, Course

admin.site.register(ClassRoom)
admin.site.register(Course)
