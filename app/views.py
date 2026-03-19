from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model


from .serializers import (
    UserSerializer,
    RegisterSerializer,
    UpdateProfileSerializer
)
from .permissions import HasResourcePermission

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(APIView):
    """POST /api/auth/login/"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'Укажите email и пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return Response({
                    'message': 'Успешный вход',
                    'user': UserSerializer(user).data
                })
            return Response(
                {'error': 'Аккаунт деактивирован'},
                status=status.HTTP_403_FORBIDDEN
            )
        return Response(
            {'error': 'Неверный email или пароль'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    """POST /api/auth/logout/"""

    def post(self, request):
        logout(request)
        return Response({'message': 'Успешный выход'})


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/auth/users/me/ - получить профиль
    PATCH /api/auth/users/me/ - обновить профиль
    DELETE /api/auth/users/me/ - мягко удалить аккаунт
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UpdateProfileSerializer
        return UserSerializer

    def perform_destroy(self, instance):
        """ Реализации мягкого удаления """
        instance.is_active = False
        instance.save()
        logout(self.request._request)


class ArticleListView(APIView):
    """
    GET /api/resources/articles/
    Просмотр списка статей (требуется право article:view)
    """
    permission_classes = [HasResourcePermission]
    resource = 'article'
    action = 'view'

    def get(self, request):
        articles = [
            {'id': 1, 'title': 'Статья 1', 'content': 'Содержание 1'},
            {'id': 2, 'title': 'Статья 2', 'content': 'Содержание 2'},
            {'id': 3, 'title': 'Статья 3', 'content': 'Содержание 3'},
        ]
        return Response({'articles': articles})


class ArticleCreateView(APIView):
    """
    POST /api/resources/articles/create/
    Создание статьи (требуется право article:create)
    """
    permission_classes = [HasResourcePermission]
    resource = 'article'
    action = 'create'

    def post(self, request):
        return Response({
            'message': 'Статья создана',
            'article': request.data
        }, status=201)


class ArticleDeleteView(APIView):
    """
    DELETE /api/resources/articles/<id>/delete/
    Удаление статьи (требуется право article:delete)
    """
    permission_classes = [HasResourcePermission]
    resource = 'article'
    action = 'delete'

    def delete(self, request, pk):
        return Response({
            'message': f'Статья {pk} удалена'
        })
