from django.db import models


class Semester(models.Model):
    """
    学期：
    2024春、2024秋等
    """
    jw_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=10, unique=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Semesters"
        ordering = ['-start_date']


class CourseType(models.Model):
    """
    课程类型：

    理论实验课
    """

    name_cn = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name_cn if self.name_cn else self.name_en or "Unnamed Course Type"

    class Meta:
        verbose_name_plural = "Course Types"
        ordering = ['name_cn']


class CourseGradation(models.Model):
    """
    课程层次：

    专业选修
    """

    name_cn = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name_cn if self.name_cn else self.name_en or "Unnamed Course Gradation"

    class Meta:
        verbose_name_plural = "Course Gradations"
        ordering = ['name_cn']


class CourseCategory(models.Model):
    """
    课程类别：

    本科计划内课程
    """

    name_cn = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name_cn if self.name_cn else self.name_en or "Unnamed Course Category"

    class Meta:
        verbose_name_plural = "Course Categories"
        ordering = ['name_cn']


class CourseClassify(models.Model):
    """
    课程范畴分类：

    科技与人文
    """

    name_cn = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name_cn if self.name_cn else self.name_en or "Unnamed Course Classify"

    class Meta:
        verbose_name_plural = "Course Classifies"
        ordering = ['name_cn']


class ExamMode(models.Model):
    """
    考试方式：

    大作业（论文、报告、项目或作品等）
    """

    name_cn = models.CharField(max_length=200, unique=True)
    name_en = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name_cn if self.name_cn else self.name_en or "Unnamed Exam Mode"

    class Meta:
        verbose_name_plural = "Exam Modes"
        ordering = ['name_cn']


class TeachLanguage(models.Model):
    """
    授课语言：

    中文
    """

    name_cn = models.CharField(max_length=50, unique=True)
    name_en = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name_cn if self.name_cn else self.name_en or "Unnamed Teach Language"

    class Meta:
        verbose_name_plural = "Teach Languages"
        ordering = ['name_cn']


class EducationLevel(models.Model):
    """
    学历层次：

    本科生
    研究生
    本研贯通
    """

    name_cn = models.CharField(max_length=50, unique=True)
    name_en = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name_cn if self.name_cn else self.name_en or "Unnamed Education Level"

    class Meta:
        verbose_name_plural = "Education Levels"
        ordering = ['name_cn']


class ClassType(models.Model):
    """
    课堂类型：

    本科生课堂类型
    （暂无）
    研究生课堂类型
    基础
    专业
    """

    name_cn = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name_cn if self.name_cn else self.name_en or "Unnamed Class Type"

    class Meta:
        verbose_name_plural = "Class Types"
        ordering = ['name_cn']


class Department(models.Model):
    """
    开课单位：

    001 数学科学学院
    200 本科生院
      108 外语教学中心
    203 物理学院
      004 近代物理系
      048 工程与应用物理系
    204 管理学院
      015 工商管理系
      017 统计与金融系
      040 项目管理教育中心
    206 化学与材料科学学院
      014 材料科学与工程系
      019 化学系
    208 地球和空间科学学院
    209 工程科学学院
      009 精密机械与精密仪器系
      013 热科学和能源工程系
    210 信息科学技术学院
      006 电子工程与信息科学系
    215 计算机科学与技术学院
      011 计算机科学与技术系
    216 公共事务学院
      041 MPA 中心 1
    219 微电子学院
    220 马克思主义学院
    221 网络空间安全学院
    240 环境科学与工程系（直属）
    910 生命科学与医学部
      207 生命科学学院
      911 附属第一医院
    """

    code = models.CharField(max_length=20, unique=True)
    name_cn = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True, null=True)
    is_college = models.BooleanField(default=False)

    def __str__(self):
        return self.name_cn if self.name_cn else self.name_en or "Unnamed Department"

    class Meta:
        verbose_name_plural = "Departments"
        ordering = ['code']


class Campus(models.Model):
    """
    校区：

    高新区
    """

    name_cn = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name_cn if self.name_cn else self.name_en or "Unnamed Campus"

    class Meta:
        verbose_name_plural = "Campuses"
        ordering = ['name_cn']


class Course(models.Model):
    """
    课程信息
    """

    jw_id = models.IntegerField(unique=True)
    code = models.CharField(max_length=20)
    name_cn = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)

    education_level = models.ForeignKey(EducationLevel, on_delete=models.SET_NULL, blank=True, null=True)
    gradation = models.ForeignKey(CourseGradation, on_delete=models.SET_NULL, blank=True, null=True)
    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, blank=True, null=True)
    class_type = models.ForeignKey(ClassType, on_delete=models.SET_NULL, blank=True, null=True)
    type = models.ForeignKey(CourseType, on_delete=models.SET_NULL, blank=True, null=True)
    classify = models.ForeignKey(CourseClassify, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name_cn}"

    class Meta:
        verbose_name_plural = "Courses"
        ordering = ['code']


class Teacher(models.Model):
    name_cn = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name_cn

    class Meta:
        verbose_name_plural = "Teachers"
        ordering = ['name_cn']


class AdminClass(models.Model):
    """
    行政班
    """

    name_cn = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name_cn

    class Meta:
        verbose_name_plural = "Admin Classes"
        ordering = ['name_cn']


class Section(models.Model):
    """
    开课信息
    """

    jw_id = models.IntegerField(unique=True)
    code = models.CharField(max_length=20)

    credits = models.FloatField(blank=True, null=True)  # 学分
    period = models.IntegerField(blank=True, null=True)  # 学时
    periods_per_week = models.IntegerField(blank=True, null=True)  # 每周学时
    std_count = models.IntegerField(blank=True, null=True)  # 选课人数
    limit_count = models.IntegerField(blank=True, null=True)  # 限选人数
    graduate_and_postgraduate = models.BooleanField(blank=True, null=True)  # 是否本研贯通

    date_time_place_text = models.TextField(blank=True, null=True)
    date_time_place_person_text = models.JSONField(blank=True, null=True)

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, blank=True, null=True)

    open_department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True)
    campus = models.ForeignKey(Campus, on_delete=models.SET_NULL, blank=True, null=True)
    exam_mode = models.ForeignKey(ExamMode, on_delete=models.SET_NULL, blank=True, null=True)
    teach_language = models.ForeignKey(TeachLanguage, on_delete=models.SET_NULL, blank=True, null=True)

    teachers = models.ManyToManyField(Teacher, related_name="sections")
    admin_classes = models.ManyToManyField(AdminClass, related_name="sections")

    def __str__(self):
        return f"{self.code} - {self.course.name_cn} - {s.name if (s := self.semester) else ''}"

    class Meta:
        verbose_name_plural = "Sections"
        ordering = ['code', 'semester__start_date']
