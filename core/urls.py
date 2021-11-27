from django.conf.urls.static import static
from django.contrib.auth.views import *
from django.urls import path
from core.views import *

urlpatterns = [
                  path('web/login/', CustomLoginView.as_view(template_name='core/auth/index.html'), name='login-web'),
                  # path('web/reset/password/', PasswordResetView.as_view(), name='password-reset'),
                  # path('web/reset/password/done', PasswordResetDoneView.as_view(), name='password_reset_done'),
                  # path('web/reset/password/confirm', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
                  # path('web/reset/password/done', PasswordResetDoneView.as_view(), name='password_reset_done'),
                  path('web/admin/', admin_index, name='admin-home'),
                  path('web/staff/', staff_index, name='staff-home'),
                  path('web/forbid/', forbid, name='forbid'),
                  path('test', testCreate, name='test'),

                  path('web/staff/create/', create_staff, name='create-staff'),
                  path('web/staff/read/', read_staffs.as_view(), name='read-staffs'),
                  path('web/staff/<int:pk>/read/', read_staff.as_view(), name='read-staff'),
                  path('web/staff/<int:pk>/update/', update_staff.as_view(), name='update-staff'),
                  path('web/staff/<int:pk>/delete/', delete_staff.as_view(), name='delete-staff'),

                  path('web/peoples/read/', read_peoples.as_view(), name='read-peoples'),
                  path('web/people/<int:pk>/read/', read_people.as_view(), name='read-people'),
                  path('web/people/<int:pk>/update/', update_people.as_view(), name='update-people'),
                  path('web/people/<int:pk>/delete/', delete_people.as_view(), name='delete-people'),

                  path('web/ngo/create/', create_ngo.as_view(), name='create-ngo'),
                  path('web/ngos/read/', read_ngos.as_view(), name='read-ngos'),
                  path('web/ngo/<int:pk>/read/', read_ngo.as_view(), name='read-ngo'),
                  path('web/ngo/<int:pk>/update/', update_ngo.as_view(), name='update-ngo'),
                  path('web/ngo/<int:pk>/delete/', delete_ngo.as_view(), name='delete-ngo'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
