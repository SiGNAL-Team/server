from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db import models
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from .serializers import *
from .views_extra import *


class BaseViewSet(viewsets.ModelViewSet):
    """Base ViewSet with common actions for all models"""

    @action(detail=False, url_path='jw-id/(?P<jw_id>[^/.]+)')
    def get_by_jw_id(self, request, jw_id=None):
        """Get object by JW ID"""
        try:
            # This will only work for models that have jw_id
            queryset = self.get_queryset()
            instance = queryset.get(jw_id=jw_id)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=404)


class CampusViewSet(viewsets.ModelViewSet):
    queryset = Campus.objects.all()
    serializer_class = CampusSerializer


class SemesterViewSet(BaseViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class CourseViewSet(BaseViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class AdminClassViewSet(viewsets.ModelViewSet):
    queryset = AdminClass.objects.all().order_by('name_cn')
    serializer_class = AdminClassSerializer


class SectionViewSet(BaseViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

    @action(detail=True, methods=['get'])
    def schedules(self, request, pk=None):
        """Get schedules for a specific section using serializer"""
        section = self.get_object()
        schedules = Schedule.objects.filter(section=section).select_related(
            'room', 'room__building', 'room__building__campus',
            'teacher', 'teacher__department', 'schedule_group', 'section__course'
        )

        # Use the serializer to format the data
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)


def home(request):
    """Home page view"""
    context = {
        'semester_count': Semester.objects.count(),
        'course_count': Course.objects.count(),
        'section_count': Section.objects.count(),
        'teacher_count': Teacher.objects.count(),
        'recent_semesters': Semester.objects.all().order_by('-start_date')[:5],
    }
    return render(request, 'ustc/home.html', context)


def semester_list(request):
    return generic_list_view(
        request, Semester, 'ustc/semester_list.html', 'semesters'
    )


def department_list(request):
    return generic_list_view(
        request, Department, 'ustc/department_list.html', 'departments'
    )


def campus_list(request):
    return generic_list_view(
        request, Campus, 'ustc/campus_list.html', 'campuses'
    )


def course_list(request):
    queryset = Course.objects.all().select_related(
        'type', 'education_level', 'gradation', 'category', 'class_type', 'classify'
    ).order_by('-jw_id')

    # Handle search and filters
    search_query = request.GET.get('q', '')
    type_filter = request.GET.get('type', '')
    education_level_filter = request.GET.get('education_level', '')

    if search_query:
        queryset = queryset.filter(
            models.Q(name_cn__icontains=search_query) |
            models.Q(name_en__icontains=search_query) |
            models.Q(code__icontains=search_query)
        )

    if type_filter:
        queryset = queryset.filter(type_id=type_filter)

    if education_level_filter:
        queryset = queryset.filter(education_level_id=education_level_filter)

    # Pagination
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Get filter options
    course_types = CourseType.objects.all()
    education_levels = EducationLevel.objects.all()

    context = {
        'courses': page_obj,
        'page_obj': page_obj,
        'course_types': course_types,
        'education_levels': education_levels,
    }
    return render(request, 'ustc/course_list.html', context)


def teacher_list(request):
    queryset = Teacher.objects.annotate(section_count=models.Count('sections')).order_by('-section_count')

    # Handle search
    search_query = request.GET.get('q', '')
    if search_query:
        queryset = queryset.filter(
            models.Q(name_cn__icontains=search_query) |
            models.Q(name_en__icontains=search_query)
        )

    paginator = Paginator(queryset, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'teachers': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'ustc/teacher_list.html', context)


def admin_class_list(request):
    return generic_list_view(
        request, AdminClass, 'ustc/admin_class_list.html', 'admin_classes'
    )


def section_list(request):
    queryset = Section.objects.all().select_related('course', 'semester').order_by('-jw_id')

    # Handle search and filters
    search_query = request.GET.get('q', '')
    semester_filter = request.GET.get('semester', '')
    department_filter = request.GET.get('department', '')

    if search_query:
        queryset = queryset.filter(
            models.Q(code__icontains=search_query) |
            models.Q(course__name_cn__icontains=search_query)
        )

    if semester_filter:
        queryset = queryset.filter(semester_id=semester_filter)

    if department_filter:
        queryset = queryset.filter(open_department_id=department_filter)

    # Pagination
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Get filter options
    semesters = Semester.objects.all().order_by('-start_date')
    departments = Department.objects.all().order_by('code')

    context = {
        'sections': page_obj,
        'page_obj': page_obj,
        'semesters': semesters,
        'departments': departments
    }
    return render(request, 'ustc/section_list.html', context)


def semester_detail(request, pk):
    semester = get_object_or_404(Semester, pk=pk)

    # Get sections for this semester
    queryset = Section.objects.filter(semester=semester).select_related('course', 'open_department', 'campus', 'exam_mode', 'teach_language')

    # Handle search
    search_query = request.GET.get('q', '')
    if search_query:
        queryset = queryset.filter(
            models.Q(code__icontains=search_query) |
            models.Q(course__name_cn__icontains=search_query) |
            models.Q(course__name_en__icontains=search_query) |
            models.Q(course__code__icontains=search_query) |
            models.Q(teachers__name_cn__icontains=search_query) |
            models.Q(teachers__name_en__icontains=search_query) |
            models.Q(open_department__name_cn__icontains=search_query) |
            models.Q(open_department__name_en__icontains=search_query)
        ).distinct()

    # Handle department filter
    department_filter = request.GET.get('department', '')
    if department_filter:
        queryset = queryset.filter(open_department_id=department_filter)

    # Handle campus filter
    campus_filter = request.GET.get('campus', '')
    if campus_filter:
        queryset = queryset.filter(campus_id=campus_filter)

    # Handle exam mode filter
    exam_mode_filter = request.GET.get('exam_mode', '')
    if exam_mode_filter:
        queryset = queryset.filter(exam_mode_id=exam_mode_filter)

    # Pagination
    paginator = Paginator(queryset, 50)  # 50 sections per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Get filter options
    departments = Department.objects.filter(
        section__semester=semester
    ).distinct().order_by('name_cn')

    campuses = Campus.objects.filter(
        section__semester=semester
    ).distinct().order_by('name_cn')

    exam_modes = ExamMode.objects.filter(
        section__semester=semester
    ).distinct().order_by('name_cn')

    context = {
        'semester': semester,
        'sections': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'departments': departments,
        'campuses': campuses,
        'exam_modes': exam_modes,
        'department_filter': department_filter,
        'campus_filter': campus_filter,
        'exam_mode_filter': exam_mode_filter,
    }

    return render(request, 'ustc/semester_detail.html', context)


def department_detail(request, pk):
    return generic_detail_view(
        request, Department, 'ustc/department_detail.html', 'department', pk=pk
    )


def campus_detail(request, pk):
    return generic_detail_view(
        request, Campus, 'ustc/campus_detail.html', 'campus', pk=pk
    )


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    # Get sections for this course, ordered by -jw_id
    sections = Section.objects.filter(course=course).order_by('-semester__start_date', '-jw_id')

    context = {
        'course': course,
        'sections': sections
    }
    return render(request, 'ustc/course_detail.html', context)


def teacher_detail(request, pk):
    return generic_detail_view(
        request, Teacher, 'ustc/teacher_detail.html', 'teacher', pk=pk
    )


def admin_class_detail(request, pk):
    return generic_detail_view(
        request, AdminClass, 'ustc/admin_class_detail.html', 'admin_class', pk=pk
    )


def section_detail(request, pk):
    section = get_object_or_404(Section, pk=pk)
    # We only load basic section data for the initial page load
    # Schedule data will be loaded asynchronously via JavaScript
    context = {
        'section': section
    }
    return render(request, 'ustc/section_detail.html', context)


def semester_detail_by_jw_id(request, jw_id):
    return generic_detail_view(
        request, Semester, 'ustc/semester_detail.html', 'semester', jw_id=jw_id
    )


def course_detail_by_jw_id(request, jw_id):
    course = get_object_or_404(Course, jw_id=jw_id)
    # Get sections for this course, ordered by -jw_id
    sections = Section.objects.filter(course=course).order_by('-jw_id')

    context = {
        'course': course,
        'sections': sections
    }
    return render(request, 'ustc/course_detail.html', context)


def section_detail_by_jw_id(request, jw_id):
    """Get section by JW ID and redirect to the main detail view"""
    # Find the section by jw_id first
    section = get_object_or_404(Section, jw_id=jw_id)
    # Redirect to the main detail view using the primary key
    return section_detail(request, pk=section.pk)
