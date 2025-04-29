# adminpanel/serializers.py

from rest_framework import serializers
from .models import ClassRoom, Course
from rest_framework import serializers
from .models import ClassRoom, Course
from users.models import User

class ClassRoomSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)  # <-- Make this field read-only

    class Meta:
        model = ClassRoom
        fields = '__all__'

from users.models import User  # Make sure you imported User

class CourseSerializer(serializers.ModelSerializer):

    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(user_type='teacher'))  # <-- FIX

    class Meta:
        model = Course
        fields = '__all__'

    def validate_teacher(self, value):
        print("Validating teacher:", value)  # Debug print
        if value.user_type != 'teacher':
            raise serializers.ValidationError("Selected user is not a teacher.")
        return value

# serializers.py
from rest_framework import serializers
from users.models import User

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone_number', 'profile_pic', 'user_type', 'otp']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.user_type = 'student'  # Ensuring the user is a student
        user.save()
        return user
