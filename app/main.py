from datetime import datetime
from typing import List, Optional


class Human:
    """Base class representing a human"""
    
    def __init__(self, name: str, age: int, email: str):
        self.name = name
        self.age = age
        self.email = email
        self.created_at = datetime.now()
    
    def introduce(self) -> str:
        return f"Hi, I'm {self.name} and I'm {self.age} years old."
    
    def get_info(self) -> dict:
        return {
            "name": self.name,
            "age": self.age,
            "email": self.email
        }


class Student(Human):
    """Student class inheriting from Human"""
    
    def __init__(self, name: str, age: int, email: str, student_id: str):
        super().__init__(name, age, email)
        self.student_id = student_id
        self.courses: List['Course'] = []
        self.grades: dict = {}
    
    def enroll_in_course(self, course: 'Course'):
        """Enroll student in a course"""
        if course not in self.courses:
            self.courses.append(course)
            course.add_student(self)
            print(f"{self.name} enrolled in {course.name}")
    
    def add_grade(self, course: 'Course', grade: float):
        """Add a grade for a course"""
        self.grades[course.name] = grade
        print(f"Grade {grade} added for {self.name} in {course.name}")
    
    def get_average_grade(self) -> float:
        """Calculate average grade"""
        if not self.grades:
            return 0.0
        return sum(self.grades.values()) / len(self.grades)
    
    def introduce(self) -> str:
        return f"Hi, I'm {self.name}, a student with ID {self.student_id}."


class Teacher(Human):
    """Teacher class inheriting from Human"""
    
    def __init__(self, name: str, age: int, email: str, subject: str, salary: float):
        super().__init__(name, age, email)
        self.subject = subject
        self.salary = salary
        self.courses: List['Course'] = []
    
    def assign_course(self, course: 'Course'):
        """Assign a course to this teacher"""
        if course not in self.courses:
            self.courses.append(course)
            course.set_teacher(self)
            print(f"{self.name} is now teaching {course.name}")
    
    def grade_student(self, student: Student, course: 'Course', grade: float):
        """Grade a student in a specific course"""
        if course in self.courses and student in course.students:
            student.add_grade(course, grade)
        else:
            print("Error: Cannot grade - student not in course or teacher not assigned")
    
    def introduce(self) -> str:
        return f"Hi, I'm {self.name}, a {self.subject} teacher."


class Course:
    """Course class"""
    
    def __init__(self, name: str, code: str, credits: int):
        self.name = name
        self.code = code
        self.credits = credits
        self.teacher: Optional[Teacher] = None
        self.students: List[Student] = []
    
    def set_teacher(self, teacher: Teacher):
        """Set the teacher for this course"""
        self.teacher = teacher
    
    def add_student(self, student: Student):
        """Add a student to the course"""
        if student not in self.students:
            self.students.append(student)
    
    def get_enrollment_count(self) -> int:
        """Get number of enrolled students"""
        return len(self.students)
    
    def get_course_info(self) -> str:
        teacher_name = self.teacher.name if self.teacher else "No teacher assigned"
        return f"Course: {self.name} ({self.code})\nTeacher: {teacher_name}\nStudents: {self.get_enrollment_count()}"


class University:
    """University class managing students, teachers, and courses"""
    
    def __init__(self, name: str, location: str):
        self.name = name
        self.location = location
        self.students: List[Student] = []
        self.teachers: List[Teacher] = []
        self.courses: List[Course] = []
    
    def add_student(self, student: Student):
        """Add a student to the university"""
        self.students.append(student)
        print(f"Student {student.name} added to {self.name}")
    
    def add_teacher(self, teacher: Teacher):
        """Add a teacher to the university"""
        self.teachers.append(teacher)
        print(f"Teacher {teacher.name} added to {self.name}")
    
    def add_course(self, course: Course):
        """Add a course to the university"""
        self.courses.append(course)
        print(f"Course {course.name} added to {self.name}")
    
    def get_statistics(self) -> dict:
        """Get university statistics"""
        return {
            "total_students": len(self.students),
            "total_teachers": len(self.teachers),
            "total_courses": len(self.courses),
            "average_student_grade": self._calculate_avg_all_students()
        }
    
    def _calculate_avg_all_students(self) -> float:
        """Calculate average grade across all students"""
        if not self.students:
            return 0.0
        total = sum(student.get_average_grade() for student in self.students)
        return total / len(self.students)
    
    def print_summary(self):
        """Print university summary"""
        print(f"\n{'='*50}")
        print(f"{self.name} - {self.location}")
        print(f"{'='*50}")
        stats = self.get_statistics()
        print(f"Students: {stats['total_students']}")
        print(f"Teachers: {stats['total_teachers']}")
        print(f"Courses: {stats['total_courses']}")
        print(f"Average Grade: {stats['average_student_grade']:.2f}")
        print(f"{'='*50}\n")


# Example usage
if __name__ == "__main__":
    # Create university
    uni = University("Tech University", "San Francisco")
    
    # Create students
    student1 = Student("Alice Johnson", 20, "alice@email.com", "S001")
    student2 = Student("Bob Smith", 22, "bob@email.com", "S002")
    student3 = Student("Charlie Brown", 21, "charlie@email.com", "S003")
    
    # Create teachers
    teacher1 = Teacher("Dr. Emma Wilson", 35, "emma@email.com", "Computer Science", 75000)
    teacher2 = Teacher("Prof. John Davis", 45, "john@email.com", "Mathematics", 80000)
    
    # Create courses
    course1 = Course("Python Programming", "CS101", 3)
    course2 = Course("Data Structures", "CS201", 4)
    course3 = Course("Calculus", "MATH101", 3)
    
    # Add to university
    uni.add_student(student1)
    uni.add_student(student2)
    uni.add_student(student3)
    uni.add_teacher(teacher1)
    uni.add_teacher(teacher2)
    uni.add_course(course1)
    uni.add_course(course2)
    uni.add_course(course3)
    
    # Assign teachers to courses
    teacher1.assign_course(course1)
    teacher1.assign_course(course2)
    teacher2.assign_course(course3)
    
    # Enroll students in courses
    student1.enroll_in_course(course1)
    student1.enroll_in_course(course3)
    student2.enroll_in_course(course1)
    student2.enroll_in_course(course2)
    student3.enroll_in_course(course2)
    student3.enroll_in_course(course3)
    
    # Grade students
    teacher1.grade_student(student1, course1, 95.0)
    teacher1.grade_student(student2, course1, 88.0)
    teacher1.grade_student(student2, course2, 92.0)
    teacher1.grade_student(student3, course2, 85.0)
    teacher2.grade_student(student1, course3, 90.0)
    teacher2.grade_student(student3, course3, 87.0)
    
    # Print information
    print("\n" + "="*50)
    print("STUDENT INTRODUCTIONS")
    print("="*50)
    print(student1.introduce())
    print(f"Average Grade: {student1.get_average_grade():.2f}")
    print(f"Enrolled in: {[c.name for c in student1.courses]}")
    print()
    print(student2.introduce())
    print(f"Average Grade: {student2.get_average_grade():.2f}")
    print(f"Enrolled in: {[c.name for c in student2.courses]}")
    
    print("\n" + "="*50)
    print("COURSE INFORMATION")
    print("="*50)
    print(course1.get_course_info())
    print()
    print(course2.get_course_info())
    
    # Print university summary
    uni.print_summary()