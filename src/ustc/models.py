from django.db import models


class CourseType(models.Model):
    """
    课程类型：

    理论实验课
    """

    name_cn = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, null=True, blank=True)


class CourseGradation(models.Model):
    """
    课程层次：

    专业选修
    """

    name_cn = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, null=True, blank=True)


class CourseCategory(models.Model):
    """
    课程类别：

    本科计划内课程
    """

    name_cn = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, null=True, blank=True)


class CourseClassify(models.Model):
    """
    课程范畴分类：

    科技与人文
    """

    name_cn = models.CharField(max_length=100, unique=True, null=True, blank=True)
    name_en = models.CharField(max_length=100, null=True, blank=True)


class ExamMode(models.Model):
    """
    考试方式：

    大作业（论文、报告、项目或作品等）
    """

    name_cn = models.CharField(max_length=200, unique=True)
    name_en = models.CharField(max_length=200, null=True, blank=True)


class TeachLanguage(models.Model):
    """
    授课语言：

    中文
    """

    name_cn = models.CharField(max_length=50, unique=True)
    name_en = models.CharField(max_length=50, null=True, blank=True)


class EducationLevel(models.Model):
    """
    学历层次：

    本科生
    研究生
    本研贯通
    """

    name_cn = models.CharField(max_length=50, unique=True)
    name_en = models.CharField(max_length=50, null=True, blank=True)


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
    name_en = models.CharField(max_length=100, null=True, blank=True)


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
    name_en = models.CharField(max_length=100, blank=True)
    is_college = models.BooleanField(default=False)


class Campus(models.Model):
    """
    校区：

    高新区
    """

    name_cn = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, blank=True)


class Course(models.Model):
    """
    课程信息
    """

    jw_id = models.IntegerField(unique=True, null=True, blank=True)
    code = models.CharField(max_length=20, unique=True)
    name_cn = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)

    type = models.ForeignKey(CourseType, on_delete=models.SET_NULL, null=True)
    gradation = models.ForeignKey(CourseGradation, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True, blank=True)
    classify = models.ForeignKey(CourseClassify, on_delete=models.SET_NULL, null=True, blank=True)

    open_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    campus = models.ForeignKey(Campus, on_delete=models.SET_NULL, null=True)

    exam_mode = models.ForeignKey(ExamMode, on_delete=models.SET_NULL, null=True)
    teach_language = models.ForeignKey(TeachLanguage, on_delete=models.SET_NULL, null=True)
    education_level = models.ForeignKey(EducationLevel, on_delete=models.SET_NULL, null=True)
    class_type = models.ForeignKey(ClassType, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.code} - {self.name_cn}"


class Teacher(models.Model):
    name_cn = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name_cn


class AdminClass(models.Model):
    """
    行政班
    """

    name_cn = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name_cn


class Section(models.Model):
    """
    开课信息
    """

    jw_id = models.IntegerField(unique=True, null=True, blank=True)
    code = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    credits = models.FloatField()  # 学分
    period = models.IntegerField()  # 学时
    periods_per_week = models.IntegerField()  # 每周学时
    std_count = models.IntegerField()  # 选课人数
    limit_count = models.IntegerField()  # 限选人数
    graduate_and_postgraduate = models.BooleanField()  # 是否本研贯通

    date_time_place_text = models.TextField(null=True, blank=True)
    date_time_place_person_text = models.JSONField(null=True, blank=True)

    teachers = models.ManyToManyField(Teacher, related_name="sections")
    admin_classes = models.ManyToManyField(AdminClass, related_name="sections")

    def __str__(self):
        return self.code
