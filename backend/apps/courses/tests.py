from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Course, Module, Content, Enrollment

User = get_user_model()

class CourseModelTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            email='teacher@example.com',
            username='teacher',
            password='testpass123',
            role=User.Role.TEACHER
        )
        self.course = Course.objects.create(
            title='Test Course',
            code='TST101',
            description='Test Description',
            credits=3
        )

    def test_create_course(self):
        self.assertEqual(self.course.title, 'Test Course')
        self.assertEqual(self.course.code, 'TST101')
        self.assertEqual(self.course.credits, 3)

    def test_create_module(self):
        module = Module.objects.create(
            course=self.course,
            title='Test Module',
            description='Test Description',
            order=1
        )
        self.assertEqual(module.course, self.course)
        self.assertEqual(module.order, 1)

class CourseAPITests(APITestCase):
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

    def test_list_courses(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get('/api/v1/courses/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_enroll_course(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            f'/api/v1/courses/courses/{self.course.id}/enroll/'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Enrollment.objects.filter(
                student=self.student,
                course=self.course
            ).exists()
        )

    def test_teacher_create_course(self):
        self.client.force_authenticate(user=self.teacher)
        course_data = {
            'title': 'New Course',
            'code': 'NEW101',
            'description': 'New Description',
            'credits': 3
        }
        response = self.client.post('/api/v1/courses/courses/', course_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)
