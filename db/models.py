import datetime
import json
import architect
from django.db import models
from django_redis import get_redis_connection
from django.core.cache import cache

from neomodel import (config, StructuredNode, StringProperty, IntegerProperty,
                      UniqueIdProperty, RelationshipTo, RelationshipFrom)

from psqlextra.types import PostgresPartitioningMethod
from psqlextra.models import PostgresPartitionedModel


class Students(models.Model):
    first_name = models.TextField()
    second_name = models.TextField()
    third_name = models.TextField(null=True)
    email = models.TextField()
    date_of_birth = models.DateField()

    def __getattribute__(self, name):
        # Set the redis_connection attribute when any method is called
        self.redis_connection = get_redis_connection()
        return super().__getattribute__(name)

    def get_from_db(self):
        return self.__class__.objects.get(pk=self.pk)

    def _get_key(self):
        key = "cache:table:{table_name}:{id}"
        return key.format(
            table_name=self.__class__.__name__.lower(),
            id=self.id
        )

    def save_to_redis(self, data=None):
        if data:
            data = {field.name: getattr(data, field.name) for field in data._meta.fields}
        else:
            data = {field.name: getattr(self, field.name) for field in self._meta.fields}
        self.redis_connection.set(self._get_key(), json.dumps(data, default=str))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.save_to_redis()

    def get(self):
        if data := self.redis_connection.get(self._get_key()):
            return json.loads(str(data))
        else:
            data = self.get_from_db()
            self.save_to_redis(data)
            return data

    def __str__(self):
        return (
            f"Имя: {self.first_name}\n"
            f"Фамилия: {self.second_name}\n"
            f"Отчество: {self.third_name}\n"
            f"Почта: {self.email}\n"
            f"Дата рождения: {self.date_of_birth}\n"
        )


class Groups(models.Model):
    name = models.TextField()
    departament_id = models.TextField()
    semester = models.IntegerField()
    student_group = models.ManyToManyField(Students, related_name='student_group')

    def __str__(self):
        return self.name


class Schedule(models.Model):
    group = models.ForeignKey("Groups", related_name='group_course', on_delete=models.CASCADE)
    lecture = models.ForeignKey("Lectures", related_name='lecture_course', on_delete=models.CASCADE)
    datetime = models.DateTimeField()


class Courses(models.Model):
    title = models.TextField()
    description = models.TextField()
    departament_id = models.TextField()
    group_course = models.ManyToManyField(Groups, related_name='group_courses')

    def __str__(self):
        return self.title


class CourseN4J(StructuredNode):
    uid = IntegerProperty(index=True, default=0)
    name = StringProperty(null=True)
    group = RelationshipTo("GroupN4J", "TO_GROUP")


class GroupN4J(StructuredNode):
    uid = IntegerProperty(index=True, default=0)
    name = StringProperty(null=True)
    # course = RelationshipFrom("CourseN4J", "FROM_COURSE")
    lecture = RelationshipTo("LectureN4J", "TO_LECTURE")
    student = RelationshipFrom("GroupN4J", "FROM_STUDENT")


class StudentN4J(StructuredNode):
    uid = IntegerProperty(index=True, default=0)
    name = StringProperty(null=True)
    group = RelationshipTo("GroupN4J", "TO_GROUP")


class LectureN4J(StructuredNode):
    uid = IntegerProperty(index=True, default=0)
    schedule = RelationshipTo("ScheduleN4J", "TO_SCHEDULE")


class ScheduleN4J(StructuredNode):
    uid = IntegerProperty(index=True, default=0)


class LecturesType(models.TextChoices):
    LECTURE = "lecture", "Lecture"
    SEMINAR = "seminar", "Seminar"


class Lectures(models.Model):
    title = models.TextField()
    tag_department = models.TextField()
    course = models.ForeignKey(Courses, related_name='lecture_course', on_delete=models.CASCADE)
    type = models.CharField(choices=LecturesType.choices, max_length=10)
    requirements = models.BooleanField()


class AttendanceStatus(models.TextChoices):
    PRESENT = "present", "Present"
    MISSING = "missing", "Missing"


class Attendance(PostgresPartitionedModel):
    class PartitioningMeta:
        method = PostgresPartitioningMethod.RANGE
        key = ["datetime"]

    student = models.ForeignKey(Students, related_name='student_attendance', on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lectures, related_name='lecture_attendance', on_delete=models.CASCADE)

    datetime = models.DateTimeField()
    status = models.CharField(choices=AttendanceStatus.choices, max_length=10)
