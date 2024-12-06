from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .models import Conversation, Message, Notification, Announcement
from .serializers import (
    ConversationSerializer, ConversationCreateSerializer,
    MessageSerializer, NotificationSerializer, AnnouncementSerializer
)
from .permissions import IsParticipant, IsAuthorOrReadOnly

class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsParticipant]
    filterset_fields = ['is_group']
    search_fields = ['name']
    ordering_fields = ['updated_at']

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        conversation = self.get_object()
        messages = conversation.messages.exclude(read_by=request.user)
        for message in messages:
            message.read_by.add(request.user)
        return Response({'status': 'messages marked as read'})

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]
    filterset_fields = ['conversation']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return Message.objects.filter(
            conversation__participants=self.request.user
        )

    def perform_create(self, serializer):
        conversation = Conversation.objects.get(
            pk=self.request.data['conversation']
        )
        serializer.save(
            sender=self.request.user,
            conversation=conversation
        )
        # Update conversation timestamp
        conversation.save()  # This updates the updated_at field

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['read', 'type']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        notifications = self.get_queryset().filter(read=False)
        notifications.update(read=True, read_at=timezone.now())
        return Response({'status': 'notifications marked as read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(read=False).count()
        return Response({'unread_count': count})

class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    filterset_fields = ['priority', 'is_active']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'start_date']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Announcement.objects.all()
        
        now = timezone.now()
        return Announcement.objects.filter(
            Q(target_roles__contains=[user.role]) &
            Q(is_active=True) &
            Q(start_date__lte=now) &
            Q(end_date__gte=now)
        )

    @action(detail=False, methods=['get'])
    def active(self, request):
        now = timezone.now()
        announcements = Announcement.objects.filter(
            Q(target_roles__contains=[request.user.role]) &
            Q(is_active=True) &
            Q(start_date__lte=now) &
            Q(end_date__gte=now)
        )
        serializer = self.get_serializer(announcements, many=True)
        return Response(serializer.data)
