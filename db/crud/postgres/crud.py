import datetime
import random
from faker import Faker
from db.models import Students, Lectures, LecturesType, Attendance, AttendanceStatus, Courses

fake = Faker("ru_RU")


class Postgres:
    def create(self, name):
        course = Courses.objects.create(
            title="",
            description="",
            departament_id=str("sdfsdf"),
        )
        lectures = []
        for _ in range(10):
            lecture = Lectures.objects.create(
                title="123",
                tag_department=0,
                course=course,
                type=random.choice([LecturesType.LECTURE]),
                requirements=random.choice([True, False]),
            )
            date_time = fake.date_time_this_decade()
            lectures.append([lecture, date_time])
        student = Students.objects.create(
            first_name=name,
            second_name="",
            email="",
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=25),
        )
        for lecture, date_time in lectures:
            attendance = Attendance.objects.create(
                student=student,
                lecture=lecture,
                datetime=date_time,
                status=random.choice([AttendanceStatus.PRESENT, AttendanceStatus.MISSING])
            )
        return student

    def read(self, student):
        for lecture in student.lectures:
            print(lecture.title)

    def update(self, student, name):
        student.name = name
        student.save()
        return student

    def delete(self, student):
        student.delete()


if __name__ == '__main__':
    postgres = Postgres()
    student = postgres.create("Романов Дмитрий")
    postgres.read(student)
    student = postgres.update(student, "Дмитрий Романов")
    postgres.delete(student)
