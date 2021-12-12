from django.conf.urls.static import static
from django.contrib.auth.views import *
from django.urls import path
from core.views import *

urlpatterns = [
                  path('web/account/login/', LoginView.as_view(
                      template_name='core/account/login.html'), name='login'),
                  path('web/account/logout/', LogoutView.as_view(
                      template_name='core/account/logged_out.html'), name='logout'),
                  path('web/account/password_change/', PasswordChangeView.as_view(
                      template_name='core/account/password_change_form.html'), name='password_change'),
                  path('web/account/password_change/done/', PasswordChangeDoneView.as_view(
                      template_name='core/account/password_change_done.html'), name='password_change_done'),
                  path('web/account/password_reset/', PasswordResetView.as_view(
                      template_name='core/account/password_reset_form.html',
                      email_template_name='core/account/password_reset_email.html'), name='password_reset'),
                  path('web/account/password_reset/done/', PasswordResetDoneView.as_view(
                      template_name='core/account/password_reset_done.html'), name='password_reset_done'),
                  path('web/account/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
                      template_name='core/account/password_reset_confirm.html'), name='password_reset_confirm'),
                  path('web/account/reset/done/', PasswordResetCompleteView.as_view(
                      template_name='core/account/password_reset_complete.html'), name='password_reset_complete'),

                  path('web/home/', home_page, name='home'),

                  path('web/admin/home', admin_home.as_view(), name='admin-home'),
                  path('web/staff/', staff_index, name='staff-home'),
                  path('web/403/<exception>', forbidden_page, name='forbid'),
                  path('web/404/<exception>', page_not_found, name='no_page'),
                  path('web/400/<exception>', bad_request, name='no_page'),

                  path('web/staff/create/', create_staff, name='create-staff'),
                  path('web/staffs/read/', read_staffs.as_view(), name='read-staffs'),
                  path('web/staff/<int:pk>/read/', read_staff.as_view(), name='read-staff'),
                  path('web/staff/<int:pk>/update/', update_staff.as_view(), name='update-staff'),
                  path('web/staff/<int:pk>/delete/', delete_staff.as_view(), name='delete-staff'),

                  path('web/peoples/read/', read_peoples.as_view(), name='read-peoples'),
                  path('web/people/<int:pk>/read/', read_people.as_view(), name='read-people'),
                  path('web/people/<int:pk>/update/', update_people.as_view(), name='update-people'),
                  path('web/people/<int:pk>/delete/', delete_people.as_view(), name='delete-people'),

                  path('web/ngo/create/', create_ngo, name='create-ngo'),
                  path('web/ngos/read/', read_ngos.as_view(), name='read-ngos'),
                  path('web/ngo/<int:pk>/read/', read_ngo.as_view(), name='read-ngo'),
                  path('web/ngo/<int:pk>/update/', update_ngo.as_view(), name='update-ngo'),
                  path('web/ngo/<int:pk>/delete/', delete_ngo.as_view(), name='delete-ngo'),

                  path('web/report/posts/', read_reports.as_view(), name='read-reports'),
                  path('web/report/<int:pk>/post/', read_report.as_view(), name='read-report'),
                  path('web/report/<int:pk>/review/', update_report.as_view(), name='review-report'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
