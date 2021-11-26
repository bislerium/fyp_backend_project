from django.conf.urls.static import static
from django.contrib.auth.views import *
from django.urls import path
from core.views import *

urlpatterns = [
                  path('web/login/', CustomLoginView.as_view(template_name='core/auth/login.html'), name='login-web'),
                  path('web/admin/', admin_index, name='admin-home'),
                  path('web/staff/', staff_index, name='staff-home'),
                  path('web/forbid/', forbid, name='forbid'),

                  path('web/staff/create/', create_staff, name='create-staff'),
                  path('web/staff/read/', read_staffs.as_view(), name='read-staffs'),
                  path('web/staff/<int:pk>/read/', read_staff.as_view(), name='read-staff'),
                  path('web/staff/<int:pk>/update/', update_staff.as_view(), name='update-staff'),
                  path('web/staff/<int:pk>/delete/', delete_staff.as_view(), name='delete-staff'),

                  path('web/users/read/', read_users.as_view(), name='read-users'),
                  path('web/user/<int:pk>/read/', read_user.as_view(), name='read-user'),
                  path('web/user/<int:pk>/update/', update_user.as_view(), name='update-user'),
                  path('web/user/<int:pk>/delete/', delete_user.as_view(), name='delete-user'),

                  path('web/ngo/create/', create_ngo.as_view(), name='create-ngo'),
                  path('web/ngos/read/', read_ngos.as_view(), name='read-ngos'),
                  path('web/ngo/<int:pk>/read/', read_ngo.as_view(), name='read-ngo'),
                  path('web/ngo/<int:pk>/update/', update_ngo.as_view(), name='update-ngo'),
                  path('web/ngo/<int:pk>/delete/', delete_ngo.as_view(), name='delete-ngo'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
