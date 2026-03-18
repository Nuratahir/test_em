from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager):
    """Переопределяем методы класса BaseUserManager
        для создания пользователей"""
    def create_user(self, email, password=None, **extra_fields):
        """Метод для создания обычного пользователя"""
        if not email:
            raise ValueError('Email должен быть указан')

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)

        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Метод для создания суперпользователя"""

        # Устанавливаем обязательные для суперпользователя флаги,
        # если они не были переданы в extra_fields
        extra_fields.setdefault('is_staff', True)  # Доступ в админку
        extra_fields.setdefault('is_superuser', True)  # Все права
        extra_fields.setdefault('is_active', True)  # Активный

        # Проверки, что флаги действительно установлены в True
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Класс для сочетания аутентификации - AbstractBaseUser
    и класс связанный с правами доступа - PermissionsMixin """
    email = models.EmailField(
        unique=True,
        verbose_name='Email адрес'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Фамилия'
    )
    patronymic = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Отчество'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Персонал'
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата регистрации'
    )

    # Привязываем кастомный менеджер к модели
    objects = UserManager()

    # Поле email используется для аутентификации вместо username
    USERNAME_FIELD = 'email'

    # При создании суперпользователя, запрос email, password
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Возвращает полное имя пользователя."""
        full_name = f"{self.last_name} {self.first_name} {self.patronymic}".strip()
        return full_name if full_name else self.email