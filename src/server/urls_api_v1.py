"""
API v1 URL configuration.

This module handles all API v1 routes for different apps.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ustc import views

# Create router for USTC app API endpoints
router = DefaultRouter()

# Register ViewSets for main models
router.register(r'semester', views.SemesterViewSet, basename='semester')
router.register(r'course', views.CourseViewSet, basename='course')
router.register(r'section', views.SectionViewSet, basename='section')
router.register(r'teacher', views.TeacherViewSet, basename='teacher')
router.register(r'department', views.DepartmentViewSet, basename='department')
router.register(r'campus', views.CampusViewSet, basename='campus')
router.register(r'admin-class', views.AdminClassViewSet, basename='admin-class')

# Register ViewSets for lookup/reference models
router.register(r'course-type', views.CourseTypeViewSet, basename='course-type')
router.register(r'course-gradation', views.CourseGradationViewSet, basename='course-gradation')
router.register(r'course-category', views.CourseCategoryViewSet, basename='course-category')
router.register(r'course-classify', views.CourseClassifyViewSet, basename='course-classify')
router.register(r'exam-mode', views.ExamModeViewSet, basename='exam-mode')
router.register(r'teach-language', views.TeachLanguageViewSet, basename='teach-language')
router.register(r'education-level', views.EducationLevelViewSet, basename='education-level')
router.register(r'class-type', views.ClassTypeViewSet, basename='class-type')

urlpatterns = [
    # Include all router URLs for USTC models
    # This automatically creates the following URL patterns:
    # 
    # For all models:
    # - GET /<model>/: List all records with optional query parameters
    # - POST /<model>/: Create a new record
    # - GET /<model>/<id>/: Fetch a specific record by internal ID
    # - PUT /<model>/<id>/: Update a specific record by internal ID
    # - PATCH /<model>/<id>/: Partially update a specific record by internal ID
    # - DELETE /<model>/<id>/: Delete a specific record by internal ID
    #
    # Main models (support jw-id lookup):
    # - semester: GET /semester/jw-id/<jw_id>/
    # - course: GET /course/jw-id/<jw_id>/
    # - section: GET /section/jw-id/<jw_id>/
    #
    # Other main models:
    # - teacher, department, campus, admin-class
    #
    # Lookup/reference models:
    # - course-type, course-gradation, course-category, course-classify
    # - exam-mode, teach-language, education-level, class-type
    path('', include(router.urls)),
]
