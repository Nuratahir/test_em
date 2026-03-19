from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Аутентификация
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Профиль
    path('users/me/', views.ProfileView.as_view(), name='profile'),

    # МОК вьюшки
    path('resources/articles/', views.ArticleListView.as_view(), name='article-list'),
    path('resources/articles/create/', views.ArticleCreateView.as_view(), name='article-create'),
    path('resources/articles/<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article-delete'),
]
