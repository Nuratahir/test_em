from rest_framework import serializers
from django.contrib.auth import get_user_model
from app.models import Role

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """ Для GET /api/auth/users/me/ """
    full_name = serializers.SerializerMethodField()
    roles = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'patronymic',
            'full_name',
            'roles',
            'is_active',
            'date_joined',
        ]
        read_only_fields = [
            'id',
            'is_active',
            'date_joined',
        ]

    def get_full_name(self, obj):
        """Возвращает полное имя пользователя"""
        return obj.get_full_name()


class RegisterSerializer(serializers.ModelSerializer):
    """Для POST /api/auth/register/"""
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        required=True,
        style={'input_type': 'password'},
        help_text='Минимальная длина пароля: 6 символов',
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='Подтверждение пароля'
    )

    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'password2',
            'first_name',
            'last_name',
            'patronymic'
        ]

    def validate(self, attrs):
        """ПРОВЕРКА ПАРОЛЕЙ"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Пароли не совпадают'})
        return attrs

    def validate_email(self, value):
        """ПРОВЕРКА EMAIL"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email уже используется')
        return value

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)

        # Назначаем роль User по умолчанию
        try:
            user_role = Role.objects.get(name='User')
            user.roles.add(user_role)
        except Role.DoesNotExist:
            pass

        return user


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Для PATCH /api/auth/users/me/"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'patronymic']

    def update(self, instance, validated_data):
        """ Обновление существующего пользователя
        instance — текущий объект из БД
        validated_data — новые данные """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.patronymic = validated_data.get('patronymic', instance.patronymic)
        instance.save()
        return instance
