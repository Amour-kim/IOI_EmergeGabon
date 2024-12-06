from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Conversation, Message, Notification, Announcement

User = get_user_model()

class MessagingModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='testpass123'
        )
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

    def test_create_message(self):
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content='Test message'
        )
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.content, 'Test message')

    def test_create_notification(self):
        notification = Notification.objects.create(
            recipient=self.user1,
            title='Test notification',
            message='Test message'
        )
        self.assertEqual(notification.recipient, self.user1)
        self.assertFalse(notification.read)

class MessagingAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user1)

    def test_create_conversation(self):
        data = {
            'participants': [self.user1.id, self.user2.id],
            'initial_message': 'Hello!'
        }
        response = self.client.post('/api/v1/messaging/conversations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 1)

    def test_send_message(self):
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)
        
        data = {
            'conversation': conversation.id,
            'content': 'Test message'
        }
        response = self.client.post('/api/v1/messaging/messages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)

    def test_create_announcement(self):
        self.user1.is_staff = True
        self.user1.save()
        
        data = {
            'title': 'Test Announcement',
            'content': 'Test content',
            'priority': 'MEDIUM',
            'target_roles': ['STUDENT'],
            'start_date': '2023-01-01T00:00:00Z',
            'end_date': '2024-01-01T00:00:00Z'
        }
        response = self.client.post('/api/v1/messaging/announcements/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Announcement.objects.count(), 1)
