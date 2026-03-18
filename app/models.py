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


class ActionPermission(models.Model):
    """ Модель разрешения: связка "ресурс: действие"
    Например: ('article', 'view') — просмотр статей
              ('article', 'create') — создание статей
              ('user', 'delete') — удаление пользователей """

    # К чему доступ
    resource = models.CharField(
        max_length=100,
        verbose_name='Ресурс',
        db_index=True
    )

    # Что можно делать
    action = models.CharField(
        max_length=50,
        verbose_name='Действие',
        db_index=True
    )

    # Описание
    name = models.CharField(
        max_length=255,
        verbose_name='Название',
        blank=True
    )

    class Meta:
        verbose_name = 'Разрешение'
        verbose_name_plural = 'Разрешения'
        # Не может быть двух записей с одинаковыми resource и action
        unique_together = ('resource', 'action')

    def __str__(self):
        return self.name or f"{self.resource}:{self.action}"

    def save(self, *args, **kwargs):
        """ мы переопределяем, чтобы поле name заполнялось автоматически
        это удобно и уменьшает вероятность ошибок """
        if not self.name:
            self.name = f"Can {self.action} {self.resource}"
        super().save(*args, **kwargs)


class Role(models.Model):
    """ Модель роли — группа разрешений.
    Например:"администратор", "модератор", "пользователь" """

    # Название роли должно быть уникальным
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Название роли'
    )

    # Связь ManyToMany с разрешениями
    # Одна роль может иметь много разрешений
    # Одно разрешение может быть во многих ролях
    permissions = models.ManyToManyField(
        ActionPermission,  # С какой моделью связь
        related_name='roles',  # Обратная связь: из разрешения получить все роли
        verbose_name='Разрешения',
        blank=True  # Роль может не иметь разрешений
    )

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.name


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

    roles = models.ManyToManyField(
        Role,  # С какой моделью связь
        related_name='users',  # Из роли получить всех пользователей с этой ролью
        blank=True,  # Пользователь может не иметь ролей
        verbose_name='Роли'
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
