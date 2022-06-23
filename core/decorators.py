from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.urls import reverse_lazy


def allowed_groups(admin: bool = False, staff: bool = False):
    def inner(func):
        @login_required(login_url=reverse_lazy('login'))
        def wrapper(request: HttpRequest, *args, **kwargs):
            user: User = request.user
            if (admin and user.is_superuser) or \
                    (user.groups.exists() and (staff and user.groups.first().name == 'Staff')):
                return func(request, *args, **kwargs)
            else:
                raise PermissionDenied

        return wrapper

    return inner
