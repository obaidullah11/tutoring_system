# adminpanel/serializers.py

from rest_framework import serializers
from .models import ClassRoom, Course

class ClassRoomSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)  # <-- Make this field read-only

    class Meta:
        model = ClassRoom
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)  # <-- Make this field read-only

    class Meta:
        model = Course
        fields = '__all__'
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
