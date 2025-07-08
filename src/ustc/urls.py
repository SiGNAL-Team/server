from django.urls import path, include
from rest_framework import routers
from . import views

app_name = 'ustc'

# Create a router for API views
router = routers.DefaultRouter()
router.register(r'semester', views.SemesterViewSet, basename='semester')
router.register(r'department', views.DepartmentViewSet, basename='department')
router.register(r'campus', views.CampusViewSet, basename='campus')
router.register(r'course', views.CourseViewSet, basename='course')
router.register(r'teacher', views.TeacherViewSet, basename='teacher')
router.register(r'admin-class', views.AdminClassViewSet, basename='admin-class')
router.register(r'section', views.SectionViewSet, basename='section')

# API URLs as per README.md (prefixed with /api/v1/)
api_urlpatterns = [
    path('api/v1/', include(router.urls)),
]

# Page URLs as per README.md
page_urlpatterns = [
    # Home page
    path('', views.home, name='home'),

    path('semester/', views.semester_list, name='semester-list'),
    path('department/', views.department_list, name='department-list'),
    path('campus/', views.campus_list, name='campus-list'),
    path('course/', views.course_list, name='course-list'),
    path('teacher/', views.teacher_list, name='teacher-list'),
    path('admin-class/', views.admin_class_list, name='admin-class-list'),
    path('section/', views.section_list, name='section-list'),

    path('semester/id/<int:pk>/', views.semester_detail, name='semester-detail'),
    path('department/id/<int:pk>/', views.department_detail, name='department-detail'),
    path('campus/id/<int:pk>/', views.campus_detail, name='campus-detail'),
    path('course/id/<int:pk>/', views.course_detail, name='course-detail'),
    path('teacher/id/<int:pk>/', views.teacher_detail, name='teacher-detail'),
    path('admin-class/id/<int:pk>/', views.admin_class_detail, name='admin-class-detail'),
    path('section/id/<int:pk>/', views.section_detail, name='section-detail'),

    path('semester/jw-id/<int:jw_id>/', views.semester_detail_by_jw_id, name='semester-detail-by-jw-id'),
    path('course/jw-id/<int:jw_id>/', views.course_detail_by_jw_id, name='course-detail-by-jw-id'),
    path('section/jw-id/<int:jw_id>/', views.section_detail_by_jw_id, name='section-detail-by-jw-id'),
]

# Combine all URL patterns
urlpatterns = api_urlpatterns + page_urlpatterns
