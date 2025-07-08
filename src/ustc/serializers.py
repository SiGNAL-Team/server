from rest_framework import serializers
from .models import (
    Semester, CourseType, CourseGradation, CourseCategory, CourseClassify,
    ExamMode, TeachLanguage, EducationLevel, ClassType, Department,
    Campus, Course, Teacher, AdminClass, Section
)


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = '__all__'


class CourseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseType
        fields = '__all__'


class CourseGradationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseGradation
        fields = '__all__'


class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = '__all__'


class CourseClassifySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseClassify
        fields = '__all__'


class ExamModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamMode
        fields = '__all__'


class TeachLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeachLanguage
        fields = '__all__'


class EducationLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationLevel
        fields = '__all__'


class ClassTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassType
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class CampusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campus
        fields = '__all__'


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'


class AdminClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminClass
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        depth = 1  # Include related objects one level deep


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'
        depth = 1  # Include related objects one level deep
