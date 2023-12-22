import random
import subprocess
import warnings
import datetime

# import g4f
import redis
import win32api
from bson import ObjectId
from django.db.models import Case, When, F, IntegerField
from django.db.models import Count
from django.db.models import Q
from django.db.models import Sum
from elasticsearch import Elasticsearch
from faker import Faker
from neomodel import clear_neo4j_database, db as n4j_db
from pymongo import MongoClient

from db.crud.elastic.crud import Elastic
from db.crud.mongo.crud import Mongo
from db.crud.postgres.crud import Postgres
from db.models import *

warnings.filterwarnings("ignore")
es = Elasticsearch([{'host': 'localhost', 'port': 9200, "scheme": "http", }], verify_certs=False)
client = MongoClient('localhost', 27017)
db = client['university_db']

collection = db['university']
fake = Faker("ru_RU")


# g4f.debug.logging = True  # Enable logging
# g4f.check_version = False  # Disable automatic version checking


def read_file(name):
    with open(name, encoding="utf-8") as file:
        data = [line.strip() for line in file.readlines()]
    return data


# def get_provider():
#     for pr in g4f.Provider.__providers__:
#         yield pr

#
# providers = get_provider()
#
# provider = next(providers)


# def gpt(content):
#     global provider
#     while True:
#         try:
#             response = g4f.ChatCompletion.create(
#                 model=g4f.models.gpt_35_turbo,
#                 provider=g4f.Provider.FakeGpt,
#                 messages=[
#                     {
#                         "role": "user",
#                         "content": content
#                     }
#                 ],
#                 stream=False,
#             )
#             return response
#         except Exception:
#             provider = next(providers)


def test_p():
    pass


def gen():
    last_time = datetime.datetime(2020, 9, 6, 0, 0, 0)
    now_time = datetime.datetime.now()

    def _win_set_time(time):
        dayOfWeek = time.isocalendar()[2]
        t = (time.year, time.month) + (dayOfWeek,) + (time.day, time.hour, time.minute, 0, 0)
        win32api.SetSystemTime(*t)

    # _win_set_time(last_time)
    command = ['venv\Scripts\python', 'manage.py', 'flush']
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate(input='yes\n'.encode())

    r = redis.Redis()
    r.flushdb()
    try:
        es.indices.delete(index="content")
    except:
        pass
    es.indices.create(index="content")
    clear_neo4j_database(n4j_db)
    # response = gpt("Напиши мне 5 рандомных названий кафедры в институте без нумерации с новой строки")
    # for res in [line.strip() for line in response.split('\n') if line.strip()]:
    #     departament = Departament(
    #         title=res
    #     )
    #     specializations = []
    #     response = gpt("Напиши мне 5 рандомных названия напралвений в институте без нумерации с новой строки")
    #     for res in [line.strip() for line in response.split('\n') if line.strip()]:
    #         specializations.append({
    #             "title": res
    #         })
    #
    #     departament.specialization = specializations
    #     departament._id = random.randint(0, 10000000)
    #     departament.save(using="mongo")

    collection.drop()
    university_data = {
        'mirea': {
            'departaments': {
                'КБ-1': {
                    '1': 'Институт кибербезопасности и цифровых технологий',
                    '2': 'Институт информационных технологий',
                },
                'КБ-2': {
                    '3': 'Институт искусственного интеллекта',
                },
                'КБ-3': {
                    '1': 'Институт кибербезопасности и цифровых технологий',
                    '3': 'Институт искусственного интеллекта',
                }
            }
        }
    }

    collection.insert_one(university_data)
    all_data = []
    result = collection.find()
    for r in result:
        all_data.append(r)

    group_year = 1
    for line in read_file("data/course.txt"):
        index = random.randint(0, len(all_data) - 1)
        course = Courses.objects.create(
            title=line,
            description=fake.paragraph(),
            departament_id=str(all_data[index]['_id']),
        )
        course_n4j = CourseN4J(uid=course.pk).save()
        group_num = 1
        for line in read_file("data/group.txt"):
            group = Groups.objects.create(
                name=f"{line}-{group_num:02}-{group_year:02}",
                departament_id=str(all_data[index]['_id']),
                semester=random.choice(range(1, 9))
            )
            group_num += 1
            group_n4j = GroupN4J(uid=group.pk).save()
            course_n4j.group.connect(group_n4j)
            course.group_course.add(group, through_defaults=None)
            lectures = []
            for _ in range(20):
                lecture = Lectures.objects.create(
                    title=fake.sentence(),
                    tag_department=random.choice(list(university_data["mirea"]["departaments"].keys())),
                    course=course,
                    type=random.choice([LecturesType.LECTURE, LecturesType.SEMINAR]),
                    requirements=random.choice([True, False]),
                )
                date_time = fake.date_time_this_decade()
                schedule = Schedule.objects.create(
                    group=group,
                    lecture=lecture,
                    datetime=date_time,
                )
                lecture_n4j = LectureN4J(uid=lecture.pk).save()
                schedule_n4j = ScheduleN4J(uid=schedule.pk).save()

                lecture_n4j.schedule.connect(schedule_n4j)

                group_n4j.lecture.connect(lecture_n4j)

                lectures.append([lecture, date_time])
                es.index(index="content", id=str(lecture.pk), document={'content': fake.paragraph()})

            for _ in range(10):
                student = Students.objects.create(
                    first_name=fake.first_name(),
                    second_name=fake.last_name(),
                    third_name=fake.first_name(),
                    email=fake.email(),
                    date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=25),
                )
                student_n4j = StudentN4J(uid=student.pk).save()
                student_n4j.group.connect(group_n4j)
                # group_n4j.student.connect(student_n4j)

                group.student_group.add(student, through_defaults=None)
                for lecture, date_time in lectures:
                    attendance = Attendance.objects.create(
                        student=student,
                        lecture=lecture,
                        datetime=date_time,
                        status=random.choice([AttendanceStatus.PRESENT, AttendanceStatus.MISSING])
                    )

        group_year += 1


def z1(search_term, start_date, end_date):
    start_date = datetime.datetime(start_date, 1, 1)
    end_date = datetime.datetime(end_date, 1, 1)

    # Students.objects.create(
    #     first_name=fake.first_name(),
    #     second_name=fake.last_name(),
    #     third_name=fake.first_name(),
    #     email=fake.email(),
    #     date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=25),
    # )
    # student = Students(id=1).get()

    resp = es.search(index="content", query={
        "match_phrase": {
            "content": search_term
        }
    })
    lectures = [int(data['_id']) for data in resp['hits']['hits']]

    schedule = Schedule.objects.filter(
        Q(lecture_id__in=lectures),
        Q(lecture__lecture_attendance__datetime__gte=start_date) &
        Q(lecture__lecture_attendance__datetime__lt=end_date)
    ).distinct()
    lectures = [sc.pk for sc in schedule]
    # students = []
    # for group in LectureN4J.nodes.filter(uid__in=lectures).group.all():
    #     students.extend([st.uid for st in group.student.all()])
    students_id = n4j_db.cypher_query(
        f'MATCH (s:StudentN4J)-[FRIEND1]-(g:GroupN4J)-[FRIEND2]-(c:LectureN4J) WHERE c.uid in {lectures} RETURN s.uid',
        resolve_objects=True
    )[0]
    students_id = [x[0] for x in students_id]
    students = Students.objects.filter(
        Q(id__in=students_id) &
        Q(student_attendance__status='missing')
    ).annotate(
        lecture_count=Count('student_attendance__lecture_id', distinct=True),
        absence_count=Count(
            'student_attendance__id',
            distinct=True
        )
    ).order_by('absence_count')[:10]

    print_data = ""
    for student in students:
        print_data += f"Студент\n" \
                      f"{student}" \
                      f"Процент посещений: {(student.lecture_count - student.absence_count) / student.lecture_count * 100:.2f}%\n" \
                      f"Период: {start_date.date()} - {end_date.date()}\n" \
                      f"Термин занятия: {search_term}\n\n"

    return print_data


def z2(semester, year):
    courses = Courses.objects.filter(
        group_course__semester=semester
    ).distinct()

    lectures = Lectures.objects.filter(course__in=courses)

    attendance_counts = Attendance.objects.filter(
        lecture__in=lectures, datetime__year=year
    ).values('lecture').annotate(
        attendance_count=Count(
            Case(When(status=AttendanceStatus.PRESENT, then=F('student')), output_field=IntegerField())),
        total_count=Count('student')
    )
    print_data = ""
    for course in courses:
        print_data += f"Курс: {course.title}\n" \
                      f"Занятия для семестра - {semester}, {year} года:\n"
        for lecture in lectures:
            lec = [
                [item['total_count'], item['attendance_count']] for item in attendance_counts if
                item['lecture'] == lecture.id
            ]
            if lec:
                total, attendance_count = lec[0]
                print_data += f"--{lecture.title:100}, Количество студентов: {total}, Количество посетивших: {attendance_count}, Требования к оборудованию: {lecture.requirements}\n"
    print_data += '\n'
    return print_data


def z3(group_name, tag_department):
    group = Groups.objects.filter(name=group_name).first()

    # students_id = n4j_db.cypher_query(
    #     f'MATCH (s:StudentN4J)-[FRIEND]-(g:GroupN4J) WHERE g.uid = {group.id} RETURN s.uid',
    #     resolve_objects=True
    # )[0]
    # students = [x[0] for x in students_id]
    #
    # attendance_info = Attendance.objects.filter(
    #     student__in=students, lecture__type='lecture',
    #     lecture__tag_department=tag_department
    # )

    schedule = Schedule.objects.filter(
        group=group, lecture__type='lecture', lecture__tag_department=tag_department
    )

    students = schedule.values(
        'group__student_group__id',  # Include student ID for grouping
        'group__student_group__first_name',
        'group__student_group__second_name',
        'group__student_group__third_name',
        'group__name',
        'group__group_courses__title'
    ).distinct()

    report_data = students.annotate(
        planned_hours=Sum(
            Case(
                When(
                    lecture__lecture_attendance__student=F('group__student_group'),
                    lecture__type='lecture', then=2)
            ), default=0
        ),

        attended_hours=Sum(
            Case(
                When(
                    lecture__lecture_attendance__status='present',
                    lecture__lecture_attendance__student=F('group__student_group'), then=2
                ), default=0,
                output_field=IntegerField()
            )
        )
    )
    print_data = ""
    dep = [_ for _ in
           collection.find(
               {"_id": ObjectId(group.departament_id), f'mirea.departaments.{tag_department}': {'$exists': True}})]

    for entry in report_data:
        print_data += f"Студент: {entry['group__student_group__first_name']} {entry['group__student_group__second_name']} {entry['group__student_group__third_name']}\n" \
                      f"Группа: {entry['group__name']}\n" \
                      f"Курс: {entry['group__group_courses__title']}\n" \
                      f"Запланировано часов: {entry['planned_hours']}\n" \
                      f"Посещено часов: {entry['attended_hours']}\n\n"

    return print_data


if __name__ == '__main__':
    gen()
