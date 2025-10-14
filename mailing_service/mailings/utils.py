from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin


class UserAccessMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if self.request.user.role == 'user':
            # Проверка на принадлежность объекта текущему пользователю
            obj = self.get_object()
            if obj.created_by != request.user:
                raise PermissionDenied("У вас нет прав доступа к этому объекту")

        return super().dispatch(request, *args, **kwargs)


class ManagerAccessMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.role != 'manager':
            raise PermissionDenied("У вас нет прав доступа")

        return super().dispatch(request, *args, **kwargs)