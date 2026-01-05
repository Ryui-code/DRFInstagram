from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .filter import PostFilterSet, UserFilterSet
from .serializers import (
FollowSerializer,
RegisterSerializer,
LoginSerializer,
PostSerializer,
PostContentSerializer,
PostLikeSerializer,
CommentSerializer,
CommentLikeSerializer
)

class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        response = Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "token": user.token,
        }, status=status.HTTP_201_CREATED)

        response.set_cookie(
            key='auth_token',
            value=user.token,
            httponly=True,
            secure=True,
            samesite='Strict'
        )
        return response

class LoginView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        response = Response({
            "id": user.id,
            "username": user.username,
            "token": user.token
        }, status=status.HTTP_200_OK)

        response.set_cookie(
            key='auth_token',
            value=user.token,
            httponly=True,
            secure=True,
            samesite='Strict'
        )
        return response

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        response = Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        response.delete_cookie("auth_token")
        return response

class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ['username']
    filterset_class = UserFilterSet

    def get_queryset(self):
        return UserProfile.objects.filter(id=self.request.user.id)

class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ['user', 'hashtag']
    filterset_class = PostFilterSet

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PostContentViewSet(viewsets.ModelViewSet):
    queryset = PostContent.objects.all()
    serializer_class = PostContentSerializer
    permission_classes = [permissions.IsAuthenticated]

class PostLikeViewSet(viewsets.ModelViewSet):
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CommentLikeViewSet(viewsets.ModelViewSet):
    queryset = CommentLike.objects.all()
    serializer_class = CommentLikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)