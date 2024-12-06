from rest_framework import serializers
from django.utils import timezone
from .models import Conversation, Message, Notification, Announcement
from apps.users.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    read_by = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ('conversation', 'sender', 'created_at', 'read_by')

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = '__all__'

    def get_last_message(self, obj):
        last_message = obj.messages.first()
        if last_message:
            return MessageSerializer(last_message).data
        return None

    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.exclude(read_by=user).count()

class ConversationCreateSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )
    initial_message = serializers.CharField(write_only=True)

    class Meta:
        model = Conversation
        fields = ('participants', 'is_group', 'name', 'initial_message')

    def create(self, validated_data):
        initial_message = validated_data.pop('initial_message')
        participants = validated_data.pop('participants')
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.set(participants)
        
        Message.objects.create(
            conversation=conversation,
            sender=self.context['request'].user,
            content=initial_message
        )
        
        return conversation

class NotificationSerializer(serializers.ModelSerializer):
    recipient = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('created_at', 'read_at')

    def update(self, instance, validated_data):
        if 'read' in validated_data and validated_data['read'] and not instance.read:
            validated_data['read_at'] = timezone.now()
        return super().update(instance, validated_data)

class AnnouncementSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'author')

    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError(
                "La date de début doit être antérieure à la date de fin."
            )
        return data

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
