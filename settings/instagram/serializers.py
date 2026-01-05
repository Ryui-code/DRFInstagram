from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
import secrets

class RegisterSerializer(serializers.ModelSerializer):
    token = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True)
    registered_date = serializers.DateField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'username',
            'password',
            'email',
            'avatar',
            'bio',
            'hashtag',
            'link',
            'registered_date',
            'token'
        ]

    def create(self, validated_data):
        validated_data['token'] = secrets.token_hex(16)
        user = UserProfile.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise ValidationError({'detail': 'Invalid credentials'})
        return {'user': user}

class LogoutSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['token']
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            raise ValidationError({'detail': 'Invalid token.'})

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = "__all__"

    def validate(self, attrs):
        if attrs['follower'] == attrs['following']:
            raise serializers.ValidationError("U can not subscribe to yourself.")
        return attrs

class PostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Post
        fields = "__all__"

class PostContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostContent
        fields = "__all__"

class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = "__all__"

    def validate(self, attrs):
        if PostLike.objects.filter(post=attrs['post'], user=attrs['user']).exists():
            raise serializers.ValidationError("U are already liked it.")
        return attrs

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = "__all__"

class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = "__all__"

    def validate(self, attrs):
        if CommentLike.objects.filter(comment=attrs['comment'], user=attrs['user']).exists():
            raise serializers.ValidationError("Like is already exists.")
        return attrs