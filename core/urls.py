import dj_rest_auth
from django.conf.urls.static import static
from django.contrib.auth.views import *
from django.urls import path, include

from core.api_views import NGODetail, PostList, PostDetail, PeopleList, PeopleDetail, BankDetail, NGOList, \
    CustomLoginView, PeopleAdd, NormalPostAdd, PollPostAdd, RequestPostAdd, ToggleUpvoteView, ToggleDownvoteView, \
    PostReportView, RequestPostParticipateView, PollPostPollView
from core.serializers import PostNormalSerializer, PostRequestSerializer, PostPollSerializer

from core.views import *

urlpatterns = [
                  # Web Endpoints
                  # URI scheme is /resource/unique-identifier/action (Credit to: https://stackoverflow.com/a/56017740)
                  # Scheme Convention:
                  #     action => (D)AREL (display*, add, remove, edit, list*) for CRUD-ing
                  #     resource => plural noun for a collection and singular noun for an item
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
                  path('web/admin/', admin_home.as_view(), name='admin-home'),
                  path('web/staff/', staff_home, name='staff-home'),
                  path('web/403/<exception>', forbidden_page, name='forbid'),
                  path('web/404/<exception>', page_not_found, name='no_page'),
                  path('web/400/<exception>', bad_request, name='no_page'),

                  # Bank as Resource
                  path('web/ngo/<int:pk>/bank/add', create_bank.as_view(), name='create-bank'),
                  path('web/Bank/<int:pk>/edit', update_bank.as_view(), name='update-bank'),
                  path('web/bank/<int:pk>/remove/', delete_bank.as_view(), name='delete-bank'),

                  # Staff as Resource
                  path('web/staffs/', read_staffs.as_view(), name='read-staffs'),
                  path('web/staffs/add/', create_staff, name='create-staff'),
                  path('web/staff/<int:pk>/', read_staff.as_view(), name='read-staff'),
                  path('web/staff/<int:pk>/edit/', update_staff.as_view(), name='update-staff'),
                  path('web/staff/<int:pk>/remove/', delete_staff.as_view(), name='delete-staff'),

                  # General People as Resource
                  path('web/peoples/', read_peoples.as_view(), name='read-peoples'),
                  path('web/people/<int:pk>/', read_people.as_view(), name='read-people'),
                  path('web/people/<int:pk>/edit/', update_people.as_view(), name='update-people'),
                  path('web/people/<int:pk>/remove/', delete_people.as_view(), name='delete-people'),

                  # NGO as Resource
                  path('web/ngos/', read_ngos.as_view(), name='read-ngos'),
                  path('web/ngos/add/', create_ngo, name='create-ngo'),
                  path('web/ngo/<int:pk>/', read_ngo.as_view(), name='read-ngo'),
                  path('web/ngo/<int:pk>/edit/', update_ngo.as_view(), name='update-ngo'),
                  path('web/ngo/<int:pk>/remove/', delete_ngo.as_view(), name='delete-ngo'),

                  # Reported Post as Resource
                  path('web/reports/', read_reports.as_view(), name='read-reports'),
                  path('web/report/<int:pk>/', read_report.as_view(), name='read-report'),
                  path('web/report/<int:pk>/review/', update_report.as_view(), name='review-report'),

                  # API Endpoints
                  # URLs that do not require a session or valid token
                  # path('api/', include('dj_rest_auth.urls')),
                  path('api/password/reset/', dj_rest_auth.views.PasswordResetView.as_view(), name='rest_password_reset'),
                  path('api/password/reset/confirm/', dj_rest_auth.views.PasswordResetConfirmView.as_view(),
                       name='rest_password_reset_confirm'),
                  path('api/login/', CustomLoginView.as_view(), name='rest_login'),
                  # URLs that require a user to be logged in with a valid session / token.
                  path('api/logout/', dj_rest_auth.views.LogoutView.as_view(), name='rest_logout'),
                  path('api/password/change/', dj_rest_auth.views.PasswordChangeView.as_view(),
                       name='rest_password_change'),
                  path('api/', include('dj_rest_auth.urls')),
                  path('api/ngos/', NGOList.as_view(), name='api-ngo-list'),
                  path('api/ngo/<int:pk>/', NGODetail.as_view(), name='api-ngo-detail'),

                  path('api/post/normal/', NormalPostAdd.as_view(), name='api-normal-post-add'),
                  path('api/post/poll/', PollPostAdd.as_view(), name='api-poll-post-add'),
                  path('api/post/request/', RequestPostAdd.as_view(), name='api-request-post-add'),
                  path('api/post/poll/', PollPostAdd.as_view(), name='api-poll-post-add'),
                  path('api/post/request/', RequestPostAdd.as_view(), name='api-request-post-add'),
                  path('api/posts/', PostList.as_view(), name='api-post-list'),
                  path('api/post/<int:post_id>/upvote/', ToggleUpvoteView.as_view(), name='api-post-upvote'),
                  path('api/post/<int:post_id>/downvote/', ToggleDownvoteView.as_view(), name='api-post-downvote'),
                  path('api/post/<int:post_id>/poll/<int:option_id>/', PollPostPollView.as_view(),
                       name='api-post-poll'),
                  path('api/post/<int:post_id>/participate/', RequestPostParticipateView.as_view(),
                       name='api-post-participate'),
                  path('api/post/<int:post_id>/report', PostReportView.as_view(), name='api-post-report'),

                  path('api/people/', PeopleList.as_view(), name='api-people-list'),
                  path('api/people/add/', PeopleAdd.as_view(), name='api-people-add'),
                  path('api/people/<int:pk>/', PeopleDetail.as_view(), name='api-people-detail'),

                  path('api/bank/<int:pk>/', BankDetail.as_view(), name='api-bank-detail'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
