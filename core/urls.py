from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import *
from django.urls import path
from django.views.generic import CreateView

from core.models import AdministrativeUser
from core.views import *

urlpatterns = [
                  path('login/', CustomLoginView.as_view(template_name='core/auth/login.html'), name='login-web'),
                  path('login/admin/<str:id>/', admin_index, name='admin-index'),
                  path('register/', create_staff, name='register-web'),
                  path('login/staff/<str:id>/', staff_index, name='staff-index'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
