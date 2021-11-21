from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import *
from django.urls import path
from django.views.generic import CreateView

from core.models import AdministrativeUser
from core.views import *

urlpatterns = [
                  path('web/login/', CustomLoginView.as_view(template_name='core/auth/login.html'), name='login-web'),
                  path('web/admin/', admin_index, name='admin-home'),
                  path('web/register/', create_staff, name='register-web'),
                  path('web/staff/', staff_index, name='staff-home'),

                  path('users/read/', read_users.as_view(), name='read-users'),
                  path('user/<int:pk>/read/', read_user.as_view(), name='read-user'),
                  path('user/<int:pk>/update/', update_user.as_view(), name='update-user'),
                  path('user/<int:pk>/delete/', delete_user.as_view(), name='delete-user'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
