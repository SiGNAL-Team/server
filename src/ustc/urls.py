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

urlpatterns = [
    # Home page
    path('', views.home, name='home'),

    path('semester/', views.semester_list, name='semester-list'),
    path('department/', views.department_list, name='department-list'),
    path('campus/', views.campus_list, name='campus-list'),
    path('course/', views.course_list, name='course-list'),
    path('teacher/', views.teacher_list, name='teacher-list'),
    path('admin-class/', views.admin_class_list, name='admin-class-list'),
    path('section/', views.section_list, name='section-list'),

    path('semester/<int:pk>/', views.semester_detail, name='semester-detail'),
    path('department/<int:pk>/', views.department_detail, name='department-detail'),
    path('campus/<int:pk>/', views.campus_detail, name='campus-detail'),
    path('course/<int:pk>/', views.course_detail, name='course-detail'),
    path('teacher/<int:pk>/', views.teacher_detail, name='teacher-detail'),
    path('admin-class/<int:pk>/', views.admin_class_detail, name='admin-class-detail'),
    path('section/<int:pk>/', views.section_detail, name='section-detail'),

    path('semester/jw-id/<int:jw_id>/', views.semester_detail_by_jw_id, name='semester-detail-by-jw-id'),
    path('course/jw-id/<int:jw_id>/', views.course_detail_by_jw_id, name='course-detail-by-jw-id'),
    path('section/jw-id/<int:jw_id>/', views.section_detail_by_jw_id, name='section-detail-by-jw-id'),

    # iCalendar routes
    path('section/<int:pk>/ical/', views.section_ical, name='section-ical'),
    path('schedule/<int:pk>/ical/', views.schedule_ical, name='schedule-ical'),
]
