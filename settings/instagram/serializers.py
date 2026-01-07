from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *

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

    def create(self, validate_data):
        user = UserProfile.objects.create_user(**validate_data)
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {'username': instance.username,
                     'email': instance.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise ValidationError({'detail': 'Invalid credentials.'})
        return {'user': user}

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance. username,
                'email': instance.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

    def validate(self, data):
        refresh_token = data.get('refresh')
        try:
            token = RefreshToken(refresh_token)
            return token
        except TokenError:
            raise serializers.ValidationError({'detail': 'Недействительный токен.'})

    def save(self):
        refresh_token = self.validated_data['refresh']
        token = RefreshToken(refresh_token)
        token.blacklist()

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