import requests_cache
from django.core.management.base import BaseCommand
from datetime import datetime
from ustc.models import (
    Course, Section, CourseType, CourseGradation, CourseCategory,
    CourseClassify, Department, Campus, ExamMode, TeachLanguage,
    EducationLevel, ClassType, Teacher, AdminClass, Semester
)


class Command(BaseCommand):
    help = "Fetches timetable JSON from the USTC catalog API and updates the database"

    def add_arguments(self, parser):
        parser.add_argument('--semester', type=str, required=False, help='The semester code to fetch data for')
        parser.add_argument('--all', action='store_true', default=False, help='Fetch all semesters')
        parser.add_argument('--no-interactive', action='store_true', default=False, help='Do not ask for interactive input')

    def handle(self, *args, **options):
        semester_code = options['semester']
        all_semesters = options['all']
        no_interactive = options['no_interactive']

        # Fetch all available semesters first
        semesters = self.fetch_and_update_semesters()

        if not semesters:
            self.stdout.write(self.style.ERROR("Failed to fetch semesters list"))
            return

        selected_semesters = []

        if all_semesters:
            selected_semesters = semesters
        elif semester_code:
            selected_semester = next((s for s in semesters if s.code == semester_code), None)
            if selected_semester:
                selected_semesters = [selected_semester]
            else:
                self.stdout.write(self.style.ERROR(f"Semester with code '{semester_code}' not found"))
                return
        elif not no_interactive:
            selected_semesters = self.interactive_semester_selection(semesters)
        else:
            # Use the most recent semester as default
            if semesters:
                most_recent = max(semesters, key=lambda s: s.id)
                selected_semesters = [most_recent]
                self.stdout.write(self.style.WARNING(f"Using most recent semester: {most_recent.name} ({most_recent.code})"))

        if not selected_semesters:
            self.stdout.write(self.style.ERROR("No semesters selected"))
            return

        # Process each selected semester
        for semester in selected_semesters:
            self.stdout.write(self.style.SUCCESS(f"Processing semester: {semester.name} ({semester.code})"))
            self.fetch_and_process_semester(semester)

    def fetch_and_update_semesters(self):
        """Fetch all available semesters from the API and update them in the database"""
        url = "https://catalog.ustc.edu.cn/api/teach/semester/list"
        self.stdout.write(f"Fetching semesters from: {url}")

        session = requests_cache.CachedSession('cache_fetch_timetable', expire_after=3600 * 24)  # Cache for 24 hours
        try:
            response = session.get(url)
            response.raise_for_status()
            data = response.json()

            semesters = []
            for item in data:
                # Parse dates or use None if invalid
                start_date = None
                end_date = None

                try:
                    if item.get("start"):
                        start_date = datetime.strptime(item["start"], "%Y-%m-%d").date()
                    if item.get("end"):
                        end_date = datetime.strptime(item["end"], "%Y-%m-%d").date()
                except ValueError:
                    self.stdout.write(self.style.WARNING(f"Invalid date format for semester {item['nameZh']}"))

                # Create or update the semester in the database
                semester, created = Semester.objects.update_or_create(
                    jw_id=item["id"],
                    defaults={
                        "name": item["nameZh"],
                        "code": item["code"],
                        "start_date": start_date,
                        "end_date": end_date,
                    }
                )

                semesters.append(semester)
                self.stdout.write(
                    f"{'Created' if created else 'Updated'} semester: {semester.name} ({semester.code})"
                )

            self.stdout.write(self.style.SUCCESS(f"Processed {len(semesters)} semesters"))
            return semesters

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching semesters: {str(e)}"))
            return []

    def interactive_semester_selection(self, semesters):
        """Allow user to interactively select semesters to process"""
        if not semesters:
            return []

        # Sort semesters by ID (typically newer ones have higher IDs)
        sorted_semesters = sorted(semesters, key=lambda s: s.id, reverse=True)

        self.stdout.write(self.style.SUCCESS("\nAvailable semesters:"))
        self.stdout.write("0. All semesters")

        # Display semester options
        for i, semester in enumerate(sorted_semesters, 1):
            self.stdout.write(f"{i}. {semester.name} ({semester.code})")

        # Add option for custom selection
        self.stdout.write(f"{len(sorted_semesters) + 1}. Custom selection (comma-separated list)")

        while True:
            self.stdout.write("\nSelect option (or 'q' to quit): ")
            choice = input().strip()

            if choice.lower() == 'q':
                return []

            try:
                choice_num = int(choice)
                if choice_num == 0:
                    return sorted_semesters
                elif 1 <= choice_num <= len(sorted_semesters):
                    return [sorted_semesters[choice_num - 1]]
                elif choice_num == len(sorted_semesters) + 1:
                    self.stdout.write("Enter comma-separated list of semester numbers: ")
                    selections = input().strip()
                    try:
                        indices = [int(x.strip()) - 1 for x in selections.split(',')]
                        selected = [sorted_semesters[i] for i in indices if 0 <= i < len(sorted_semesters)]
                        return selected
                    except (ValueError, IndexError):
                        self.stdout.write(self.style.ERROR("Invalid selection, please try again"))
                else:
                    self.stdout.write(self.style.ERROR("Invalid option, please try again"))
            except ValueError:
                self.stdout.write(self.style.ERROR("Please enter a number or 'q' to quit"))

    def fetch_and_process_semester(self, semester):
        """Fetch and process all sections for a semester"""
        self.stdout.write(f"Fetching data for semester: {semester.name} ({semester.code})")

        url = f"https://catalog.ustc.edu.cn/api/teach/lesson/list-for-teach/{semester.jw_id}"
        sections_count = self.fetch_and_process_data(url, semester)

        self.stdout.write(self.style.SUCCESS(f"Total sections processed for {semester.name}: {sections_count}"))

    def fetch_and_process_data(self, url, semester=None):
        """Fetch data from a URL and process all sections"""
        self.stdout.write(f"Fetching data from: {url}")
        session = requests_cache.CachedSession('cache_fetch_timetable', expire_after=3600)

        try:
            response = session.get(url)
            response.raise_for_status()
            data = response.json()

            self.stdout.write(f"Fetched {len(data)} sections")

            for item in data:
                self.import_section(item, semester)

            return len(data)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching data from {url}: {str(e)}"))
            return 0

    def update_or_create_fk(self, model, name_cn, name_en=None, **kwargs):
        if not name_cn:
            return None
        result, _ = model.objects.update_or_create(
            name_cn=name_cn,
            defaults={**kwargs, "name_en": name_en or ""}
        )
        return result

    def update_or_create_department(self, dept_json):
        department, _ = Department.objects.update_or_create(
            code=dept_json["code"],
            defaults={
                "name_cn": dept_json["cn"],
                "name_en": dept_json.get("en", ""),
                "is_college": dept_json.get("college", False)
            }
        )
        return department

    def get_or_create_department_by_code(self, code):
        if not code:
            return None

        department, _ = Department.objects.get_or_create(
            code=code,
            defaults={"name_cn": f"未知({code})"}
        )
        return department

    def import_section(self, item, semester=None):
        # Step 1: Course-level fields
        course_info = item["course"]
        course, _ = Course.objects.update_or_create(
            jw_id=course_info["id"],
            defaults={
                "jw_id": course_info["id"],
                "code": course_info["code"],
                "name_cn": course_info["cn"],
                "name_en": course_info.get("en", ""),
                "type": self.update_or_create_fk(CourseType, item["courseType"]["cn"], item["courseType"]["en"]),
                "gradation": self.update_or_create_fk(CourseGradation, item["courseGradation"]["cn"], item["courseGradation"]["en"]),
                "category": self.update_or_create_fk(CourseCategory, item["courseCategory"]["cn"], item["courseCategory"]["en"]),
                "classify": self.update_or_create_fk(CourseClassify, item["courseClassify"]["cn"], item["courseClassify"]["en"]),
                "class_type": self.update_or_create_fk(ClassType, item["classType"]["cn"], item["classType"]["en"]),
                "education_level": self.update_or_create_fk(EducationLevel, item["education"]["cn"], item["education"]["en"]),
            }
        )

        # Step 2: Section-level info
        section, created = Section.objects.update_or_create(
            jw_id=item["id"],
            defaults={
                "jw_id": item.get("id", None),
                "code": item.get("code", None),
                "credits": item.get("credits", 0),
                "period": item.get("period", 0),
                "periods_per_week": item.get("periodsPerWeek", 0),
                "std_count": item.get("stdCount", 0),
                "limit_count": item.get("limitCount", 0),
                "graduate_and_postgraduate": item.get("graduateAndPostgraduate", False),
                "date_time_place_text": item.get("dateTimePlaceText"),
                "date_time_place_person_text": item.get("dateTimePlacePersonText", {}),
                "course": course,
                "semester": semester,
                "open_department": self.update_or_create_department(item["openDepartment"]),
                "campus": self.update_or_create_fk(Campus, item["campus"]["cn"], item["campus"]["en"]),
                "exam_mode": self.update_or_create_fk(ExamMode, item["examMode"]["cn"], item["examMode"]["en"]),
                "teach_language": self.update_or_create_fk(TeachLanguage, item["teachLang"]["cn"], item["teachLang"]["en"]),
            }
        )

        # Step 3: Teachers
        section.teachers.clear()
        for t in item.get("teacherAssignmentList", []):
            teacher, _ = Teacher.objects.update_or_create(
                name_cn=t["cn"],
                name_en=t.get("en", ""),
                department=self.get_or_create_department_by_code(t.get("departmentCode"))
            )
            section.teachers.add(teacher)

        # Step 4: Admin Classes
        section.admin_classes.clear()
        for c in item.get("adminClasses", []):
            admin_class, _ = AdminClass.objects.update_or_create(
                name_cn=c["cn"],
                defaults={"name_en": c.get("en", "")}
            )
            section.admin_classes.add(admin_class)

        self.stdout.write(f"{'Created' if created else 'Updated'} section: {section.code}")
