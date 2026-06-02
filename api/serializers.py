from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import UserProfile
from portal.models import (
    Category, Exam, Job, Scheme, Scholarship, Result, Notification,
    ForumPost, ForumComment
)

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source='state.name', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'phone', 'qualification', 'state', 'state_name', 'occupation',
            'gender', 'age', 'annual_income', 'notification_email',
            'notification_browser', 'notification_sms'
        ]

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_citizen', 'is_moderator', 'is_admin_user', 'profile']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Exam
        fields = '__all__'

class JobSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source='state.name', read_only=True)

    class Meta:
        model = Job
        fields = '__all__'

class SchemeSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source='state.name', read_only=True)

    class Meta:
        model = Scheme
        fields = '__all__'

class ScholarshipSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source='state.name', read_only=True)

    class Meta:
        model = Scholarship
        fields = '__all__'

class ResultSerializer(serializers.ModelSerializer):
    exam_name = serializers.CharField(source='exam.name', read_only=True)

    class Meta:
        model = Result
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class ForumCommentSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='author.email', read_only=True)
    upvote_count = serializers.IntegerField(source='upvotes.count', read_only=True)

    class Meta:
        model = ForumComment
        fields = ['id', 'post', 'content', 'author_email', 'created_at', 'upvote_count']

class ForumPostSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='author.email', read_only=True)
    upvote_count = serializers.IntegerField(source='upvotes.count', read_only=True)
    downvote_count = serializers.IntegerField(source='downvotes.count', read_only=True)
    comments = ForumCommentSerializer(many=True, read_only=True)

    class Meta:
        model = ForumPost
        fields = [
            'id', 'title', 'content', 'author_email', 'created_at',
            'upvote_count', 'downvote_count', 'is_verified', 'comments'
        ]
