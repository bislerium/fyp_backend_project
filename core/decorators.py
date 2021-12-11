from django.http import HttpRequest
from django.shortcuts import redirect


def allowed_groups(*groups: str):
    def inner(func):
        def wrapper(request: HttpRequest, *args, **kwargs):
            user_ = request.user
            if 'Admin' in groups and user_.is_staff and user_.is_superuser:
                return func(request, *args, **kwargs)
            user_group = user_.groups
            if user_group.exists():
                group = request.user.groups.first().name
                if group in groups:
                    return func(request, *args, **kwargs)
            return redirect('forbid')
        return wrapper
    return inner
