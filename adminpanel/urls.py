# adminpanel/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # ClassRoom URLs
    path('classrooms/', views.ClassRoomListCreateAPIView.as_view(), name='classroom-list-create'),
    path('classrooms/<int:pk>/', views.ClassRoomRetrieveUpdateDestroyAPIView.as_view(), name='classroom-detail'),

    # Course URLs
    path('courses/', views.CourseListCreateAPIView.as_view(), name='course-list-create'),
    path('courses/<int:pk>/', views.CourseRetrieveUpdateDestroyAPIView.as_view(), name='course-detail'),
    # path('create_student/', views.CreateStudentView.as_view(), name='create_student'),

]
