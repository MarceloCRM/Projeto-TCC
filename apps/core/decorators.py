from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from functools import wraps

def role_admin_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a superuser
    or belongs to the 'Admin' group, raising PermissionDenied if not.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or request.user.groups.filter(name='Admin').exists():
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("Você não tem permissão para acessar esta página.")
    return _wrapped_view
