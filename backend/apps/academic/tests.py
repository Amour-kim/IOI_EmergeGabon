from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import AcademicYear, Semester, Grade, Attendance
from apps.courses.models import Course

User = get_user_model()

class AcademicModelTests(TestCase):
    def setUp(self):
        self.academic_year = AcademicYear.objects.create(
            year='2023-2024',
            start_date='2023-09-01',
            end_date='2024-06-30'
        )
        self.semester = Semester.objects.create(
            academic_year=self.academic_year,
            number=1,
            start_date='2023-09-01',
            end_date='2024-01-31'
        )

    def test_create_academic_year(self):
        self.assertEqual(self.academic_year.year, '2023-2024')
        self.assertFalse(self.academic_year.is_current)

    def test_create_semester(self):
        self.assertEqual(self.semester.number, 1)
        self.assertEqual(self.semester.academic_year, self.academic_year)

    def test_set_current_academic_year(self):
        self.academic_year.is_current = True
        self.academic_year.save()
        self.assertTrue(
            AcademicYear.objects.get(id=self.academic_year.id).is_current
        )

class AcademicAPITests(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            email='teacher@example.com',
            username='teacher',
            password='testpass123',
            role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(
            email='student@example.com',
            username='student',
            password='testpass123',
            role=User.Role.STUDENT
        )
        self.course = Course.objects.create(
            title='Test Course',
            code='TST101',
            description='Test Description',
            credits=3
        )
        self.academic_year = AcademicYear.objects.create(
            year='2023-2024',
            start_date='2023-09-01',
            end_date='2024-06-30'
        )
        self.semester = Semester.objects.create(
            academic_year=self.academic_year,
            number=1,
            start_date='2023-09-01',
            end_date='2024-01-31'
        )

    def test_create_grade(self):
        self.client.force_authenticate(user=self.teacher)
        grade_data = {
            'student_id': self.student.id,
            'course_id': self.course.id,
            'semester_id': self.semester.id,
            'score': 15.5,
            'comment': 'Good work'
        }
        response = self.client.post('/api/v1/academic/grades/', grade_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_mark_attendance(self):
        self.client.force_authenticate(user=self.teacher)
        attendance_data = {
            'student_id': self.student.id,
            'course_id': self.course.id,
            'date': '2023-09-15',
            'is_present': True
        }
        response = self.client.post('/api/v1/academic/attendance/', attendance_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_student_view_grades(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/v1/academic/grades/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
