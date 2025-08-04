import requests_cache
import logging
from django.core.management.base import BaseCommand
from datetime import datetime
from ustc.models import (
    Course, Section, CourseType, CourseGradation, CourseCategory,
    CourseClassify, Department, Campus, ExamMode, TeachLanguage,
    EducationLevel, ClassType, Teacher, AdminClass, Semester
)


class Command(BaseCommand):
    help = "Fetches timetable JSON from the USTC catalog API and updates the database"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = requests_cache.CachedSession('cache_fetch_timetable', expire_after=60 * 60 * 24)  # Cache for 24 hours
        self.logger = logging.getLogger('ustc.fetch_timetable')
        self.setup_logging()

    def setup_logging(self):
        """Configure logging for the command"""
        if self.logger.handlers:
            self.logger.handlers.clear()

        handler = logging.StreamHandler(self.stdout)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)

        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False  # Prevent duplicate logs

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', default=False, help='Fetch all semesters')
        parser.add_argument('--quiet', action='store_true', default=False, help='Suppress detailed output')
        parser.add_argument('--log-level', default='INFO',
                            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                            help='Set the logging level explicitly')
        # Django automatically adds --verbosity

    def handle(self, *args, **options):
        if options.get('quiet'):
            self.logger.setLevel(logging.WARNING)
        elif options.get('log_level'):
            log_level = options['log_level']
            self.logger.setLevel(getattr(logging, log_level))

        self.logger.debug("Debug logging is enabled")

        semesters = self.fetch_and_update_semesters()

        if not semesters:
            self.logger.error("Failed to fetch semesters list")
            return

        if not options['all']:
            # Use the most recent semester as default
            most_recent = max(semesters, key=lambda s: s.id)
            self.logger.warning(f"Using most recent semester: {most_recent.name} ({most_recent.code})")
            semesters = [most_recent]

        for semester in semesters:
            self.logger.info(f"Processing semester: {semester.name} ({semester.code})")
            self.fetch_and_process_semester(semester)

    def fetch_and_update_semesters(self):
        """Fetch all available semesters from the API and update them in the database"""
        url = "https://catalog.ustc.edu.cn/api/teach/semester/list"
        self.logger.info(f"Fetching semesters from: {url}")

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            self.logger.error(f"Failed to fetch semesters: {e}", exc_info=True)
            return []

        semesters = []
        created_count = updated_count = 0

        try:
            for item in data:
                semester, created = Semester.objects.update_or_create(
                    jw_id=item["id"],
                    defaults={
                        "name": item["nameZh"],
                        "code": item["code"],
                        "start_date": datetime.strptime(item["start"], "%Y-%m-%d").date(),
                        "end_date": datetime.strptime(item["end"], "%Y-%m-%d").date()
                    }
                )

                semesters.append(semester)

                if created:
                    created_count += 1
                    self.logger.debug(f"Created semester: {semester.name} ({semester.code})")
                else:
                    updated_count += 1
                    self.logger.debug(f"Updated semester: {semester.name} ({semester.code})")
        except Exception as e:
            self.logger.error(f"Error processing semester data: {e}", exc_info=True)

        self.logger.info(f"Processed {len(semesters)} semesters (Created: {created_count}, Updated: {updated_count})")
        return semesters

    def fetch_and_process_semester(self, semester):
        """Fetch and process all sections for a semester"""
        self.logger.info(f"Fetching data for semester: {semester.name} ({semester.code})")

        url = f"https://catalog.ustc.edu.cn/api/teach/lesson/list-for-teach/{semester.jw_id}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            self.logger.info(f"Fetched {len(data)} sections")
        except Exception as e:
            self.logger.error(f"Failed to fetch sections for semester {semester.name}: {e}", exc_info=True)
            return

        # Use a counter to show progress periodically
        created_count = updated_count = error_count = 0
        total_count = len(data)
        progress_interval = max(1, total_count // 10)  # Report progress at 10% intervals

        for i, item in enumerate(data, 1):
            try:
                result = self.import_section(item, semester)

                if result == 'created':
                    created_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                error_count += 1
                section_id = item.get('id', 'unknown')
                self.logger.error(f"Error processing section ID {section_id}: {e}")
                continue

            if i % progress_interval == 0 or i == total_count:
                self.logger.info(f"Progress: {i}/{total_count} sections processed ({i / total_count:.1%})")

        self.logger.info(
            f"Total sections processed for {semester.name}: {total_count} "
            f"(Created: {created_count}, Updated: {updated_count}, Errors: {error_count})"
        )

    def import_section(self, item, semester):
        from django.db import transaction

        def update_or_create_fk(model, name_cn, name_en=None, **kwargs):
            if not name_cn:
                return None

            result, _ = model.objects.update_or_create(
                name_cn=name_cn,
                defaults={**kwargs, "name_en": name_en or ""}
            )
            return result

        def update_or_create_department(dept_json):
            department, _ = Department.objects.update_or_create(
                code=dept_json["code"],
                defaults={
                    "name_cn": dept_json["cn"],
                    "name_en": dept_json.get("en", ""),
                    "is_college": dept_json.get("college", False)
                }
            )
            return department

        def get_or_create_department_by_code(code):
            if not code:
                return None

            department, _ = Department.objects.get_or_create(
                code=code,
                defaults={"name_cn": f"未知({code})"}
            )
            return department

        # Wrap all database operations in a transaction
        with transaction.atomic():
            try:
                # Step 1: Course-level fields
                course_info = item["course"]
                course, _ = Course.objects.update_or_create(
                    jw_id=course_info["id"],
                    defaults={
                        "education_level": update_or_create_fk(EducationLevel, item["education"]["cn"], item["education"]["en"]),
                        "gradation": update_or_create_fk(CourseGradation, item["courseGradation"]["cn"], item["courseGradation"]["en"]),
                        "category": update_or_create_fk(CourseCategory, item["courseCategory"]["cn"], item["courseCategory"]["en"]),
                        "class_type": update_or_create_fk(ClassType, item["classType"]["cn"], item["classType"]["en"]),
                        "type": update_or_create_fk(CourseType, item["courseType"]["cn"], item["courseType"]["en"]),
                        "classify": update_or_create_fk(CourseClassify, item["courseClassify"]["cn"], item["courseClassify"]["en"]),

                        "code": course_info["code"],
                        "name_cn": course_info["cn"],
                        "name_en": course_info.get("en", ""),
                    }
                )

                # Step 2: Section-level info
                section, created = Section.objects.update_or_create(
                    jw_id=item["id"],
                    defaults={
                        "course": course,
                        "semester": semester,
                        "open_department": update_or_create_department(item["openDepartment"]),
                        "campus": update_or_create_fk(Campus, item["campus"]["cn"], item["campus"]["en"]),
                        "exam_mode": update_or_create_fk(ExamMode, item["examMode"]["cn"], item["examMode"]["en"]),
                        "teach_language": update_or_create_fk(TeachLanguage, item["teachLang"]["cn"], item["teachLang"]["en"]),

                        "code": item.get("code", None),
                        "credits": item.get("credits", 0),
                        "period": item.get("period", 0),
                        "periods_per_week": item.get("periodsPerWeek", 0),
                        "std_count": item.get("stdCount", 0),
                        "limit_count": item.get("limitCount", 0),
                        "graduate_and_postgraduate": item.get("graduateAndPostgraduate", False),
                        "date_time_place_text": item.get("dateTimePlaceText"),
                        "date_time_place_person_text": item.get("dateTimePlacePersonText", {}),
                    }
                )

                # Step 3: Teachers - Use bulk operations for better performance
                teacher_list = []
                section.teachers.clear()
                for t in item.get("teacherAssignmentList", []):
                    teacher, _ = Teacher.objects.update_or_create(
                        name_cn=t["cn"],
                        name_en=t.get("en", ""),
                        department=get_or_create_department_by_code(t.get("departmentCode"))
                    )
                    teacher_list.append(teacher)

                if teacher_list:
                    section.teachers.add(*teacher_list)

                # Step 4: Admin Classes - Use bulk operations for better performance
                admin_class_list = []
                section.admin_classes.clear()
                for c in item.get("adminClasses", []):
                    admin_class, _ = AdminClass.objects.update_or_create(
                        name_cn=c["cn"],
                        defaults={"name_en": c.get("en", "")}
                    )
                    admin_class_list.append(admin_class)

                if admin_class_list:
                    section.admin_classes.add(*admin_class_list)

                self.logger.debug(f"{'Created' if created else 'Updated'} section: {section.code}")
                return 'created' if created else 'updated'

            except Exception as e:
                # Log the specific error but re-raise to trigger transaction rollback
                self.logger.error(f"Error in transaction for section {item.get('id')}: {e}")
                raise
