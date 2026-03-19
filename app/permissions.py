from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied, NotAuthenticated


class HasResourcePermission(BasePermission):
    """
    Кастомный класс разрешения для проверки доступа к ресурсу.
    - resource (строка) - название ресурса
    - action (строка) - действие
    """

    def has_permission(self, request, view):
        """
        Проверка прав доступа.
        Вызывается для всех запросов к view.
        """
        # Проверка аутентификации
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated('Требуется аутентификация')

        # Суперпользователь имеет доступ ко всему
        if request.user.is_superuser:
            return True

        # Получаем resource и action из view
        resource = getattr(view, 'resource', None)
        action = getattr(view, 'action', None)

        if not resource or not action:
            return True

        # 4. Проверяем наличие права у пользователя
        if self._check_permission(request.user, resource, action):
            return True

        # 5. Если нет права - 403 Forbidden
        raise PermissionDenied(f'Нет права на {action} ресурса {resource}')

    def _check_permission(self, user, resource, action):
        """Внутренний метод проверки наличия права у пользователя."""
        # Собираем все разрешения из всех ролей пользователя
        user_permissions = set()
        for role in user.roles.all():
            for perm in role.permissions.all():
                user_permissions.add((perm.resource, perm.action))

        # Проверяем наличие нужной пары (resource, action)
        return (resource, action) in user_permissions