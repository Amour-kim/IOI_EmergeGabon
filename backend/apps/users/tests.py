from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import StudentProfile, TeacherProfile

User = get_user_model()

class UserModelTests(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': User.Role.STUDENT
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_create_user(self):
        self.assertEqual(self.user.email, self.user_data['email'])
        self.assertEqual(self.user.role, User.Role.STUDENT)
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

    def test_create_student_profile(self):
        student_profile = StudentProfile.objects.get(user=self.user)
        self.assertIsNotNone(student_profile)
        self.assertTrue(student_profile.student_id.startswith('STD'))

    def test_user_str_method(self):
        expected_str = f"{self.user.get_full_name()} ({self.user.email})"
        self.assertEqual(str(self.user), expected_str)

class UserAPITests(APITestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': User.Role.STUDENT
        }
        self.user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=self.user)

    def test_get_user_list(self):
        response = self.client.get('/api/v1/users/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_detail(self):
        response = self.client.get(f'/api/v1/users/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email'])

    def test_update_user(self):
        new_data = {'first_name': 'Updated'}
        response = self.client.patch(
            f'/api/v1/users/users/{self.user.id}/',
            new_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], new_data['first_name'])
