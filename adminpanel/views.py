# adminpanel/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  
from .models import ClassRoom, Course
from .serializers import ClassRoomSerializer, CourseSerializer
# from users.serializers import StudentSerializer  # <-- Un-comment and import properly
from rest_framework import status, views

# Helper function for standardized response
def custom_response(success, message, data=None, status_code=status.HTTP_200_OK):
    print(f"custom_response -> success: {success}, message: {message}")  # <-- Add print
    return Response({
        "success": success,
        "message": message,
        "data": data
    }, status=status_code)

# ClassRoom APIs
class ClassRoomListCreateAPIView(generics.ListCreateAPIView):
    queryset = ClassRoom.objects.all()
    serializer_class = ClassRoomSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        print("Fetching list of ClassRooms")  # <-- Add print
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(True, "Classrooms fetched successfully", serializer.data)

    def perform_create(self, serializer):
        print(f"Creating ClassRoom by user: {self.request.user}")  # <-- Add print
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        print(f"Received ClassRoom create request with data: {request.data}")  # <-- Add print
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return custom_response(True, "Classroom created successfully", serializer.data, status.HTTP_201_CREATED)

class ClassRoomRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClassRoom.objects.all()
    serializer_class = ClassRoomSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        print(f"Retrieving ClassRoom with ID: {kwargs.get('pk')}")  # <-- Add print
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return custom_response(True, "Classroom retrieved successfully", serializer.data)

    def update(self, request, *args, **kwargs):
        print(f"Updating ClassRoom with ID: {kwargs.get('pk')} and data: {request.data}")  # <-- Add print
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return custom_response(True, "Classroom updated successfully", serializer.data)

    def destroy(self, request, *args, **kwargs):
        print(f"Deleting ClassRoom with ID: {kwargs.get('pk')}")  # <-- Add print
        instance = self.get_object()
        self.perform_destroy(instance)
        return custom_response(True, "Classroom deleted successfully", None)

class CourseListCreateAPIView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        print("Received Course list request")
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        print("Fetched Courses:", serializer.data)
        return custom_response(True, "Courses fetched successfully", serializer.data)

    def perform_create(self, serializer):
        print("Performing Course creation with user:", self.request.user)
        serializer.save()

    def create(self, request, *args, **kwargs):
        print("Received Course create request with data:", request.data)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            print("Course serializer is valid")
            self.perform_create(serializer)
            print("Course created successfully")
            return custom_response(True, "Course created successfully", serializer.data, status.HTTP_201_CREATED)
        else:
            print("Course serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CourseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        print(f"Retrieving Course with ID: {kwargs.get('pk')}")  # <-- Add print
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return custom_response(True, "Course retrieved successfully", serializer.data)

    def update(self, request, *args, **kwargs):
        print(f"Updating Course with ID: {kwargs.get('pk')} and data: {request.data}")  # <-- Add print
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return custom_response(True, "Course updated successfully", serializer.data)

    def destroy(self, request, *args, **kwargs):
        print(f"Deleting Course with ID: {kwargs.get('pk')}")  # <-- Add print
        instance = self.get_object()
        self.perform_destroy(instance)
        return custom_response(True, "Course deleted successfully", None)

# Create Student API
class CreateStudentView(views.APIView):
    def post(self, request):
        print(f"Received Create Student request with data: {request.data}")  # <-- Add print
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.save()
            print(f"Student created successfully with ID: {student.id}")  # <-- Add print
            return Response({"message": "Student created successfully", "student_id": student.id}, status=status.HTTP_201_CREATED)
        else:
            print(f"Validation errors while creating student: {serializer.errors}")  # <-- Add print
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
