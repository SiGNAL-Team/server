from django.contrib import admin
from .models import *


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_cn', 'name_en']
    search_fields = ['name_cn', 'name_en']


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
