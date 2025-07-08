from django.contrib import admin
from .models import *


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'start_date', 'end_date']
    list_filter = ['name']
    search_fields = ['name', 'code']


@admin.register(CourseType)
class CourseTypeAdmin(admin.ModelAdmin):
    list_display = ['name_cn', 'name_en']
    search_fields = ['name_cn', 'name_en']


@admin.register(CourseGradation)
class CourseGradationAdmin(admin.ModelAdmin):
    list_display = ['name_cn', 'name_en']
    search_fields = ['name_cn', 'name_en']


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name_cn', 'name_en']
    search_fields = ['name_cn', 'name_en']


@admin.register(CourseClassify)
class CourseClassifyAdmin(admin.ModelAdmin):
    list_display = ['name_cn', 'name_en']
    search_fields = ['name_cn', 'name_en']


@admin.register(ExamMode)
class ExamModeAdmin(admin.ModelAdmin):
    list_display = ['name_cn', 'name_en']
    search_fields = ['name_cn', 'name_en']


@admin.register(TeachLanguage)
class TeachLanguageAdmin(admin.ModelAdmin):
    list_display = ['name_cn', 'name_en']
    search_fields = ['name_cn', 'name_en']


@admin.register(EducationLevel)
class EducationLevelAdmin(admin.ModelAdmin):
    list_display = ['name_cn', 'name_en']
    search_fields = ['name_cn', 'name_en']


@admin.register(ClassType)
class ClassTypeAdmin(admin.ModelAdmin):
    list_display = ['name_cn', 'name_en']
    search_fields = ['name_cn', 'name_en']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_cn', 'name_en', 'is_college']
    list_filter = ['is_college']
    search_fields = ['code', 'name_cn', 'name_en']


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ['name_cn', 'name_en']
    search_fields = ['name_cn', 'name_en']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'jw_id', 'name_cn', 'name_en', 'education_level', 'gradation', 'category', 'class_type', 'type', 'classify']
    list_filter = ['type', 'gradation', 'category', 'classify', 'education_level', 'class_type']
    search_fields = ['code', 'name_cn', 'name_en']


class TeacherSectionInline(admin.TabularInline):
    model = Section.teachers.through
    verbose_name = "Teaching Section"
    verbose_name_plural = "Teaching Sections"
    extra = 0

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('section', 'teacher')

    fields = ['get_section_details']
    readonly_fields = ['get_section_details']

    @admin.display(description='Section Details')
    def get_section_details(self, obj):
        section = obj.section
        course = section.course
        semester_name = section.semester.name if section.semester else 'N/A'
        credits = section.credits if section.credits else 'N/A'
        return f"{section.code} - {course.name_cn} ({semester_name}) - Credits: {credits}"


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['name_cn', 'name_en', 'department', 'count_sections']
    list_filter = ['department']
    search_fields = ['name_cn', 'name_en']
    inlines = [TeacherSectionInline]

    @admin.display(description='Sections Count')
    def count_sections(self, obj):
        return obj.sections.count()


@admin.register(AdminClass)
class AdminClassAdmin(admin.ModelAdmin):
    list_display = ['name_cn', 'name_en']
    search_fields = ['name_cn', 'name_en']


class SectionTeacherInline(admin.TabularInline):
    model = Section.teachers.through
    verbose_name = "Teacher"
    verbose_name_plural = "Teachers"
    extra = 1


class SectionAdminClassInline(admin.TabularInline):
    model = Section.admin_classes.through
    verbose_name = "Admin Class"
    verbose_name_plural = "Admin Classes"
    extra = 1


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['code', 'jw_id', 'get_course_code', 'get_course_name', 'semester', 'credits', 'periods_per_week', 'std_count', 'limit_count', 'open_department', 'campus', 'teach_language', 'exam_mode', 'graduate_and_postgraduate']
    list_filter = ['semester', 'graduate_and_postgraduate', 'course__type', 'course__education_level', 'open_department', 'campus', 'exam_mode', 'teach_language']
    search_fields = ['code', 'course__name_cn', 'course__name_en', 'course__code']
    exclude = ['teachers', 'admin_classes']  # Hide these fields since we're using inlines
    inlines = [SectionTeacherInline, SectionAdminClassInline]

    @admin.display(description='Course Code', ordering='course__code')
    def get_course_code(self, obj):
        return obj.course.code

    @admin.display(description='Course Name', ordering='course__name_cn')
    def get_course_name(self, obj):
        return obj.course.name_cn
