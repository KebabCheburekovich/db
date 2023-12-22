from db.models import StudentN4J, GroupN4J, CourseN4J


class N4J:
    def create_student(self, name):
        return StudentN4J(name=name).save()

    def create_group(self, name):
        return GroupN4J(name=name).save()

    def add_student_to_group(self, student, group):
        student.group.connect(group)

    def create_course(self, name):
        return CourseN4J(name=name).save()

    def add_group_to_course(self, group, course):
        course.group.connect(group)

    def update_person(self, student: StudentN4J, new_name):
        student.name = new_name
        return student.save()

    def delete_student(self, student: StudentN4J):
        student.delete()

    # def read_student(self, student: StudentN4J):
    #     return StudentN4J


if __name__ == "__main__":
    neo4j = N4J()
    student = neo4j.create_student("Романов Дмитрий")
    group = neo4j.create_group("БСБО-17-20")
    course = neo4j.create_course("IT")
    neo4j.add_student_to_group(student, group)
    neo4j.add_group_to_course(group, course)

    student = neo4j.update_person(student, "Дмитрий Романов")
    neo4j.delete_student(student)
