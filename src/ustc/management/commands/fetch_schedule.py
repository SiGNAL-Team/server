import requests_cache
import json
import logging
from django.core.management.base import BaseCommand
from ustc.models import Section, Schedule, ScheduleGroup, Room, Teacher, Building, Campus, Semester
from ustc.models_extra import RoomType
from django.db import transaction


class Command(BaseCommand):
    help = "Fetches schedule data for sections in groups of 50 and commits to the database"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = requests_cache.CachedSession('cache_fetch_schedule', expire_after=60 * 60 * 24)  # Cache for 24 hours
        self.logger = logging.getLogger('ustc.fetch_schedule')
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

    def handle(self, *args, **options):
        if options.get('quiet'):
            self.logger.setLevel(logging.WARNING)
        elif options.get('log_level'):
            log_level = options['log_level']
            self.logger.setLevel(getattr(logging, log_level))

        self.logger.debug("Debug logging is enabled")

        # Get all available semesters
        self.logger.info("Getting available semesters...")
        semesters = Semester.objects.all().order_by('-id')

        if not semesters:
            self.logger.error("No semesters found in database")
            return

        # If --all not specified, use only the most recent semester
        if not options['all']:
            semesters = semesters[:1]
            self.logger.warning(f"Using most recent semester: {semesters[0].name} ({semesters[0].code})")
        else:
            self.logger.info(f"Processing all {semesters.count()} semesters")

        self.logger.info("Please enter cookies for the request (key=value pairs, separated by semicolons):")
        cookies_input = input().strip()
        self.cookies = {k.strip(): v.strip() for k, v in (pair.split('=') for pair in cookies_input.split(';'))}
        self.logger.debug(f"Cookies parsed with {len(self.cookies)} key-value pairs")

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:140.0) Gecko/20100101 Firefox/140.0",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-GPC": "1",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }
        self.logger.debug("HTTP headers configured")

        # Process each selected semester
        for semester in semesters:
            self.logger.info(f"Processing semester: {semester.name} ({semester.code})")

            # Get all section IDs for this semester
            self.logger.info(f"Starting schedule data fetch for semester {semester.name}...")
            section_ids = list(Section.objects.filter(semester=semester).values_list('jw_id', flat=True))
            self.logger.info(f"Found {len(section_ids)} sections to process for semester {semester.name}")

            if not section_ids:
                self.logger.warning(f"No sections found for semester {semester.name}, skipping")
                continue

            self.process_section_ids(section_ids)

    def process_section_ids(self, section_ids):
        """Process a list of section IDs to fetch and update schedule data"""
        section_ids = sorted(section_ids)[::-1]  # Ensure section IDs are sorted
        self.logger.debug("Section IDs sorted in reverse order")

        # Divide section IDs into groups
        LEN = 100
        section_id_groups = [section_ids[i:i + LEN] for i in range(0, len(section_ids), LEN)]
        self.logger.info(f"Divided into {len(section_id_groups)} groups of up to {LEN} sections each")

        url = "https://jw.ustc.edu.cn/ws/schedule-table/datum"
        self.logger.debug(f"Using API endpoint: {url}")
        self.logger.debug("Using requests_cache with 24-hour expiration")

        # Track progress
        total_groups = len(section_id_groups)
        processed_sections = 0
        total_sections = len(section_ids)

        for i, group in enumerate(section_id_groups, 1):
            self.logger.info(f"Processing group {i}/{total_groups} with {len(group)} sections " +
                             f"(Overall progress: {processed_sections}/{total_sections} sections, {processed_sections / total_sections:.1%})")

            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"Section IDs in this group: {group}")

            processed_sections += len(group)

            try:
                self.logger.debug(f"Sending POST request to {url}")
                response = self.session.post(
                    url,
                    headers=self.headers,
                    cookies=self.cookies,
                    data=json.dumps({"lessonIds": group})
                )
                response.raise_for_status()
                data = response.json()
                self.logger.debug(f"Received response with status {response.status_code}")

                self.parse_and_commit(data)
                self.logger.info(f"Completed processing group {i}/{total_groups}")

            except Exception as e:
                self.logger.error(f"Error fetching data for group {i}/{total_groups}: {str(e)}", exc_info=True)

    def create_or_update_campus(self, campus_data):
        if not campus_data:
            self.logger.debug("Empty campus data received, returning None")
            return None

        campus_name = campus_data.get("nameZh")
        if not campus_name:
            self.logger.debug("No campus name provided in campus data, returning None")
            return None

        campus_id = campus_data.get("id")
        self.logger.debug(f"Processing campus: {campus_name} (jw_id: {campus_id})")

        if campus_id:
            # If we have a jw_id, use it as the primary lookup
            campus, created = Campus.objects.update_or_create(
                jw_id=campus_id,
                defaults={
                    "name_cn": campus_name,
                    "name_en": campus_data.get("nameEn"),
                }
            )
        else:
            # Fall back to using name_cn if no jw_id is available
            self.logger.warning(f"No jw_id for campus {campus_name}, using name_cn as lookup key")
            campus, created = Campus.objects.update_or_create(
                name_cn=campus_name,
                defaults={
                    "name_en": campus_data.get("nameEn"),
                }
            )

        if created:
            self.logger.info(f"Created new Campus: {campus_name} (jw_id: {campus_id})")
        else:
            self.logger.debug(f"Updated existing Campus: {campus_name} (jw_id: {campus_id})")

        return campus

    def create_or_update_building(self, building_data):
        if not building_data:
            self.logger.debug("Empty building data received, returning None")
            return None

        building_name = building_data.get("nameZh")
        building_id = building_data.get("id")
        self.logger.debug(f"Processing building: {building_name} (jw_id: {building_id})")

        # Process campus data if available
        self.logger.debug("Processing campus for building")
        campus = self.create_or_update_campus(building_data.get("campus"))

        building, created = Building.objects.update_or_create(
            jw_id=building_id,
            defaults={
                "code": building_data.get("code"),
                "name_cn": building_name,
                "name_en": building_data.get("nameEn"),
                "campus": campus
            }
        )

        if created:
            self.logger.info(f"Created new Building: {building_name} (jw_id: {building_id})")
        else:
            self.logger.debug(f"Updated existing Building: {building_name} (jw_id: {building_id})")

        return building

    def create_or_update_room_type(self, room_type_data):
        if not room_type_data:
            self.logger.debug("Empty room type data received, returning None")
            return None

        room_type_name = room_type_data.get("nameZh")
        room_type_id = room_type_data.get("id")
        self.logger.debug(f"Processing room type: {room_type_name} (jw_id: {room_type_id})")

        room_type, created = RoomType.objects.update_or_create(
            jw_id=room_type_id,
            defaults={
                "code": room_type_data.get("code"),
                "name_cn": room_type_name,
                "name_en": room_type_data.get("nameEn"),
            }
        )

        if created:
            self.logger.info(f"Created new RoomType: {room_type_name} (jw_id: {room_type_id})")
        else:
            self.logger.debug(f"Updated existing RoomType: {room_type_name} (jw_id: {room_type_id})")

        return room_type

    def create_or_update_room(self, room_data):
        if not room_data:
            self.logger.debug("Empty room data received, returning None")
            return None

        room_name = room_data.get("nameZh")
        room_id = room_data.get("id")
        self.logger.debug(f"Processing room: {room_name} (jw_id: {room_id})")

        self.logger.debug("Processing building for room")
        building = self.create_or_update_building(room_data.get("building"))

        self.logger.debug("Processing room type for room")
        room_type = self.create_or_update_room_type(room_data.get("roomType"))

        room, created = Room.objects.update_or_create(
            jw_id=room_id,
            defaults={
                "code": room_data.get("code"),
                "name_cn": room_name,
                "name_en": room_data.get("nameEn"),
                "floor": room_data.get("floor"),
                "virtual": room_data.get("virtual", False),
                "seats_for_section": room_data.get("seatsForLesson"),
                "remark": room_data.get("remark"),
                "seats": room_data.get("seats", 0),
                "building": building,
                "room_type": room_type
            }
        )

        if created:
            self.logger.info(f"Created new Room: {room_name} (jw_id: {room_id})")
        else:
            self.logger.debug(f"Updated existing Room: {room_name} (jw_id: {room_id})")

        return room

    def create_or_update_teacher(self, teacher_id, person_id, person_name):
        self.logger.debug(f"Processing teacher: {person_name} (teacher_id: {teacher_id})")

        teacher = Teacher.objects.filter(person_id=person_id).first()
        if not teacher:
            teacher = Teacher.objects.filter(name_cn=person_name, person_id__isnull=True).first()

        if not teacher:
            self.logger.debug(f"Teacher with person_id={person_id} not found, creating new record")
            teacher, created = Teacher.objects.update_or_create(
                person_id=person_id,
                defaults={
                    "name_cn": person_name,
                    "teacher_id": teacher_id,
                    "person_id": person_id,
                    "department": None
                }
            )
            if created:
                self.logger.info(f"Created new Teacher: {person_name} (teacher_id: {teacher_id})")
            else:
                self.logger.debug(f"Updated existing Teacher: {person_name} (teacher_id: {teacher_id})")
        else:
            teacher.person_id = person_id
            teacher.teacher_id = teacher_id
            teacher.name_cn = person_name
            self.logger.debug(f"Found existing Teacher: {person_name} (teacher_id: {teacher_id})")

        return teacher

    def create_or_update_schedule_group(self, group_data, section):
        if not group_data or not section:
            self.logger.debug("Missing group data or section, returning None")
            return None

        group_id = group_data.get("id")
        group_no = group_data.get("no")

        self.logger.debug(f"Processing schedule group #{group_no} for section {section.code} (jw_id: {group_id})")

        schedule_group, created = ScheduleGroup.objects.update_or_create(
            jw_id=group_id,
            defaults={
                "section": section,
                "no": group_no,
                "limit_count": group_data.get("limitCount"),
                "std_count": group_data.get("stdCount"),
                "actual_periods": group_data.get("actualPeriods"),
                "default": group_data.get("default", False)
            }
        )

        if created:
            self.logger.info(f"Created new Schedule Group #{group_no} for {section.code} (jw_id: {group_id})")
        else:
            self.logger.debug(f"Updated existing Schedule Group #{group_no} for {section.code} (jw_id: {group_id})")

        return schedule_group

    def create_or_update_schedule(self, schedule_data, section):
        if not schedule_data or not section:
            self.logger.debug("Missing schedule data or section, returning None")
            return None

        date = schedule_data.get("date")
        weekday = schedule_data.get("weekday")
        schedule_group_id = schedule_data.get("scheduleGroupId")

        self.logger.debug(f"Processing schedule for section {section.code} on {date} (weekday: {weekday})")

        self.logger.debug("Processing room for schedule")
        room = self.create_or_update_room(schedule_data.get("room"))

        self.logger.debug("Processing teacher for schedule")
        teacher = self.create_or_update_teacher(
            teacher_id=schedule_data.get("teacherId"),
            person_id=schedule_data.get("personId"),
            person_name=schedule_data.get("personName"),
        )

        self.logger.debug(f"Looking up schedule group with jw_id: {schedule_group_id}")
        schedule_group = ScheduleGroup.objects.filter(jw_id=schedule_group_id).first()
        if not schedule_group:
            self.logger.warning(f"Schedule group with jw_id {schedule_group_id} not found")

        # Simply create a new schedule entry
        schedule = Schedule.objects.create(
            section=section,
            schedule_group=schedule_group,
            room=room,
            teacher=teacher,
            periods=schedule_data.get("periods"),
            date=date,
            weekday=weekday,
            start_time=schedule_data.get("startTime"),
            end_time=schedule_data.get("endTime"),
            experiment=schedule_data.get("experiment"),
            custom_place=schedule_data.get("customPlace"),
            lesson_type=schedule_data.get("lessonType"),
            week_index=schedule_data.get("weekIndex"),
            exercise_class=schedule_data.get("exerciseClass") or False,
            start_unit=schedule_data.get("startUnit"),
            end_unit=schedule_data.get("endUnit")
        )

        self.logger.info(f"Created new Schedule for {section.code} on {date} (weekday: {weekday})")

        return schedule

    def parse_and_commit(self, data):
        """Parse the JSON response and commit to the database"""

        result = data.get("result", {})

        lesson_list = result.get("lessonList", [])
        schedule_group_list = result.get("scheduleGroupList", [])
        schedule_list = result.get("scheduleList", [])

        self.logger.info(f"Processing data with {len(lesson_list)} lessons, {len(schedule_group_list)} schedule groups, and {len(schedule_list)} schedules")

        processed_sections = 0
        missing_sections = 0

        for lesson in lesson_list:
            section_id = lesson.get("id")
            self.logger.debug(f"Processing lesson with ID: {section_id}")

            section = Section.objects.filter(jw_id=section_id).first()
            if not section:
                self.logger.warning(f"Section with ID {section_id} not found in database")
                missing_sections += 1
                continue

            # update teacher info related to this section
            teacher_mapping: dict[str, dict] = {}
            for teacher_data in lesson.get('teacherAssignmentList', []):
                teacher_mapping[teacher_data['name']] = teacher_data

            for teacher in section.teachers.all():
                if (teacher_data := teacher_mapping.get(teacher.name_cn)) is not None:
                    teacher.person_id = teacher_data.get("personId")
                    teacher.teacher_id = teacher_data.get("teacherId")
                    teacher.save()
                    self.logger.debug(f"Updated teacher {teacher.name_cn} with person_id {teacher.person_id} and teacher_id {teacher.teacher_id}")

            self.logger.debug(f"Found section: {section.code} (jw_id: {section_id})")
            processed_sections += 1

            # Process scheduleGroupList and scheduleList in a transaction
            try:
                with transaction.atomic():
                    # Process scheduleGroupList
                    groups_count = 0
                    for group in schedule_group_list:
                        if group.get("lessonId") == section_id:
                            self.logger.debug(f"Processing schedule group for section ID: {section_id}")
                            self.create_or_update_schedule_group(group, section)
                            groups_count += 1
                    self.logger.debug(f"Processed {groups_count} schedule groups for section {section.code}")

                    # First, delete all existing schedules for this section
                    deleted_count = Schedule.objects.filter(section=section).delete()[0]
                    self.logger.debug(f"Deleted {deleted_count} existing schedules for section {section.code}")

                    # Process scheduleList and create new schedules
                    schedules_count = 0
                    for schedule_data in schedule_list:
                        if schedule_data.get("lessonId") == section_id:
                            self.logger.debug(f"Creating new schedule for section ID: {section_id}")
                            self.create_or_update_schedule(schedule_data, section)
                            schedules_count += 1
                    self.logger.debug(f"Created {schedules_count} new schedules for section {section.code}")
            except Exception as e:
                self.logger.error(f"Error processing section {section.code}: {str(e)}")
                continue

        self.logger.info(f"Successfully processed {processed_sections} sections, {missing_sections} sections not found")
        if missing_sections > 0:
            self.logger.warning(f"{missing_sections} sections were not found in database")
