from rest_framework import serializers
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from .models import (
    Community, CommunityMembership, MembershipRequest,
    Discussion, Comment, Tag, Report
)
from apps.users.serializers import UserSerializer

class TagSerializer(serializers.ModelSerializer):
    usage_count = serializers.IntegerField(source='get_usage_count', read_only=True)

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('slug',)

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)

class CommunitySerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    member_count = serializers.IntegerField(source='get_member_count', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_member = serializers.SerializerMethodField()
    pending_requests_count = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = '__all__'
        read_only_fields = ('slug', 'creator')

    def get_is_member(self, obj):
        user = self.context['request'].user
        return obj.is_member(user)

    def get_pending_requests_count(self, obj):
        if obj.requires_approval:
            return obj.get_pending_requests().count()
        return 0

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)

class CommunityMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    community = CommunitySerializer(read_only=True)
    invited_by = UserSerializer(read_only=True)
    is_ban_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = CommunityMembership
        fields = '__all__'
        read_only_fields = ('joined_at',)

    def validate(self, data):
        if data.get('is_banned') and not data.get('ban_reason'):
            raise serializers.ValidationError(
                "Une raison est requise pour le bannissement."
            )
        return data

class MembershipRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    community = CommunitySerializer(read_only=True)
    handled_by = UserSerializer(read_only=True)

    class Meta:
        model = MembershipRequest
        fields = '__all__'
        read_only_fields = ('status', 'handled_by', 'handled_at')

    def validate(self, data):
        user = self.context['request'].user
        community = data['community']

        if community.is_member(user):
            raise serializers.ValidationError(
                "Vous êtes déjà membre de cette communauté."
            )

        if MembershipRequest.objects.filter(
            user=user,
            community=community,
            status=MembershipRequest.Status.PENDING
        ).exists():
            raise serializers.ValidationError(
                "Vous avez déjà une demande en attente pour cette communauté."
            )

        return data

class DiscussionSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    community = CommunitySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Discussion
        fields = '__all__'
        read_only_fields = ('views_count', 'last_activity')

    def get_comments_count(self, obj):
        return obj.comments.count()

    def validate(self, data):
        user = self.context['request'].user
        community = data['community']

        if not community.is_member(user):
            raise serializers.ValidationError(
                "Vous devez être membre de la communauté pour créer une discussion."
            )

        if community.is_private and not user.is_staff:
            membership = CommunityMembership.objects.get(
                user=user,
                community=community
            )
            if membership.is_banned:
                raise serializers.ValidationError(
                    "Vous êtes banni de cette communauté."
                )

        return data

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('is_edited', 'edited_at')

    def get_replies(self, obj):
        if obj.parent is None:  # Only get replies for parent comments
            return CommentSerializer(
                obj.replies.all(),
                many=True,
                context=self.context
            ).data
        return []

    def validate(self, data):
        user = self.context['request'].user
        discussion = data['discussion']
        community = discussion.community

        if not community.is_member(user):
            raise serializers.ValidationError(
                "Vous devez être membre de la communauté pour commenter."
            )

        if discussion.is_locked:
            raise serializers.ValidationError(
                "Cette discussion est verrouillée."
            )

        if community.is_private and not user.is_staff:
            membership = CommunityMembership.objects.get(
                user=user,
                community=community
            )
            if membership.is_banned:
                raise serializers.ValidationError(
                    "Vous êtes banni de cette communauté."
                )

        return data

class ReportSerializer(serializers.ModelSerializer):
    reporter = UserSerializer(read_only=True)
    community = CommunitySerializer(read_only=True)
    handled_by = UserSerializer(read_only=True)
    reported_content = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ('status', 'handled_by', 'handled_at')

    def get_reported_content(self, obj):
        """Obtenir le contenu signalé"""
        content_type = obj.content_type
        model_class = content_type.model_class()
        try:
            instance = model_class.objects.get(id=obj.object_id)
            if obj.report_type == Report.ReportType.DISCUSSION:
                return {
                    'type': 'discussion',
                    'title': instance.title,
                    'author': UserSerializer(instance.author).data
                }
            elif obj.report_type == Report.ReportType.COMMENT:
                return {
                    'type': 'comment',
                    'content': instance.content[:100],
                    'author': UserSerializer(instance.author).data
                }
            elif obj.report_type == Report.ReportType.USER:
                return {
                    'type': 'user',
                    'user': UserSerializer(instance).data
                }
        except model_class.DoesNotExist:
            return None

    def validate(self, data):
        user = self.context['request'].user
        community = data['community']

        if not community.is_member(user):
            raise serializers.ValidationError(
                "Vous devez être membre de la communauté pour faire un signalement."
            )

        # Vérifier si l'utilisateur n'a pas déjà signalé ce contenu
        existing_report = Report.objects.filter(
            reporter=user,
            content_type=data['content_type'],
            object_id=data['object_id'],
            status=Report.Status.PENDING
        ).exists()

        if existing_report:
            raise serializers.ValidationError(
                "Vous avez déjà signalé ce contenu."
            )

        return data
