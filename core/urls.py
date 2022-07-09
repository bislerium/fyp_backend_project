import dj_rest_auth.views as rest_view
from django.conf.urls.static import static
from django.contrib.auth.views import *
from django.urls import path, re_path

from core.api_views import NGODetail, PostList, PostDetail, PeopleList, PeopleDetail, BankDetail, NGOList, \
    PeopleAdd, NormalPostAdd, PollPostAdd, RequestPostAdd, ToggleUpvoteView, ToggleDownvoteView, \
    PostReportView, RequestPostParticipateView, PollPostPollView, RelatedOptionList, TokenVerification, NGOOptionList, \
    UserPostList, PeopleRUD, PostRetrieveUpdateDelete, CustomAPILoginView
from core.serializers import CustomPasswordResetSerializer
from core.views import *

urlpatterns = [
                  # Web Endpoints---------------------------------------------------------------------------------------
                  # URI scheme is /resource/unique-identifier/action (Credit to: https://stackoverflow.com/a/56017740)
                  # Scheme Convention:
                  #     action => (D)AREL (display*, add, remove, edit, list*) for CRUD-ing
                  #     resource => plural noun for a collection and singular noun for an item
                  path('', home, name='default'),

                  path('ping/', ping_test, name='ping_test'),
                  path('app/', app_landing_page, name='app-landing-page'),
                  path('app/coming-soon', coming_soon_page, name='coming-soon'),

                  path('web/account/login/', CustomWebLoginView.as_view(
                      template_name='core/account/login.html'), name='login'),
                  path('web/account/logout/', LogoutView.as_view(
                      template_name='core/account/logged_out.html'), name='logout'),
                  path('web/account/password_change/', PasswordChangeView.as_view(
                      template_name='core/account/password_change_form.html'), name='password_change'),
                  path('web/account/password_change/done/', PasswordChangeDoneView.as_view(
                      template_name='core/account/password_change_done.html'), name='password_change_done'),
                  path('web/account/password_reset/', PasswordResetView.as_view(
                      template_name='core/account/password_reset_form.html',
                      html_email_template_name='core/account/password_reset_email.html'), name='password_reset'),
                  path('web/account/password_reset/done/', PasswordResetDoneView.as_view(
                      template_name='core/account/password_reset_done.html'), name='password_reset_done'),
                  path('web/account/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
                      template_name='core/account/password_reset_confirm.html'), name='password_reset_confirm'),
                  path('web/account/reset/done/', PasswordResetCompleteView.as_view(
                      template_name='core/account/password_reset_complete.html'), name='password_reset_complete'),

                  path('web/home/', home_page_router, name='home-page-router'),
                  path('web/admin/', AdminHome.as_view(), name='admin-home'),
                  path('web/staff/', staff_home, name='staff-home'),

                  # For Testing Web Exceptions, Disable at production
                  # path('web/403/<exception>', forbidden_page, name='403'),
                  # path('web/404/<exception>', page_not_found, name='404'),
                  # path('web/400/<exception>', bad_request, name='400'),
                  path('web/500/<exception>', server_error, name='500'),

                  # Bank as Resource
                  path('web/ngo/<int:pk>/bank/add', BankCreate.as_view(), name='create-bank'),
                  path('web/Bank/<int:pk>/edit', BankUpdate.as_view(), name='update-bank'),
                  path('web/bank/<int:pk>/remove/', BankDelete.as_view(), name='delete-bank'),

                  # Staff as Resource
                  path('web/staffs/', StaffsRead.as_view(), name='read-staffs'),
                  path('web/staffs/add/', create_staff, name='create-staff'),
                  path('web/staff/<int:pk>/', StaffRead.as_view(), name='read-staff'),
                  path('web/staff/<int:pk>/', StaffRead.as_view(), name='read-staff'),
                  path('web/staff/<int:pk>/edit/', StaffUpdate.as_view(), name='update-staff'),
                  path('web/staff/<int:pk>/remove/', StaffDelete.as_view(), name='delete-staff'),

                  # General People as Resource
                  path('web/peoples/', PeoplesRead.as_view(), name='read-peoples'),
                  path('web/people/<int:pk>/', PeopleRead.as_view(), name='read-people'),
                  path('web/people/<int:pk>/edit/', PeopleUpdate.as_view(), name='update-people'),
                  path('web/people/<int:pk>/remove/', PeopleDelete.as_view(), name='delete-people'),

                  # NGO as Resource
                  path('web/ngos/', NGOsRead.as_view(), name='read-ngos'),
                  path('web/ngos/add/', create_ngo, name='create-ngo'),
                  path('web/ngo/<int:pk>/', NGORead.as_view(), name='read-ngo'),
                  path('web/ngo/<int:pk>/edit/', NGOUpdate.as_view(), name='update-ngo'),
                  path('web/ngo/<int:pk>/remove/', NGODelete.as_view(), name='delete-ngo'),

                  # Reported Post as Resource
                  path('web/reports/', ReportsRead.as_view(), name='read-reports'),
                  path('web/report/<int:pk>/', ReportRead.as_view(), name='read-report'),
                  path('web/report/<int:pk>/review/', ReportUpdate.as_view(), name='review-report'),

                  # API Endpoints --------------------------------------------------------------------------------------
                  # URLs that do not require a session or valid token
                  # path('api/', include('dj_rest_auth.urls')),
                  path('api/password/reset/', rest_view.PasswordResetView.as_view(
                      serializer_class=CustomPasswordResetSerializer), name='rest_password_reset'),
                  path('api/password/reset/confirm/', rest_view.PasswordResetConfirmView.as_view(),
                       name='rest_password_reset_confirm'),
                  path('api/login/', CustomAPILoginView.as_view(), name='rest_login'),
                  # URLs that require a general to be logged in with a valid session / token.
                  path('api/logout/', rest_view.LogoutView.as_view(), name='rest_logout'),
                  path('api/password/change/', rest_view.PasswordChangeView.as_view(),
                       name='rest_password_change'),
                  path('api/general/verify/', TokenVerification.as_view(), name='token-verify'),

                  re_path(r'^api/(?P<user_type>(ngo|people))/(?P<user_id>\d+)/posts/$', UserPostList.as_view(),
                          name='api-general-post-list'),
                  path('api/ngos/', NGOList.as_view(), name='api-ngo-list'),
                  path('api/ngo/<int:pk>/', NGODetail.as_view(), name='api-ngo-detail'),

                  path('api/post/normal/', NormalPostAdd.as_view(), name='api-normal-post-add'),
                  path('api/post/poll/', PollPostAdd.as_view(), name='api-poll-post-add'),
                  path('api/post/request/', RequestPostAdd.as_view(), name='api-request-post-add'),
                  path('api/posts/', PostList.as_view(), name='api-post-list'),
                  path('api/post/<int:pk>/', PostDetail.as_view(), name='api-post-detail'),
                  path('api/post/<int:post_id>/detail/', PostRetrieveUpdateDelete.as_view(),
                       name='api-post-update-detail'),
                  path('api/post/<int:post_id>/update/', PostRetrieveUpdateDelete.as_view(), name='api-post-update'),
                  path('api/post/<int:post_id>/delete/', PostRetrieveUpdateDelete.as_view(), name='api-post-delete'),
                  path('api/post/<int:post_id>/upvote/', ToggleUpvoteView.as_view(), name='api-post-upvote'),
                  path('api/post/<int:post_id>/downvote/', ToggleDownvoteView.as_view(), name='api-post-downvote'),
                  path('api/post/<int:post_id>/poll/<int:option_id>/', PollPostPollView.as_view(),
                       name='api-post-poll'),
                  path('api/post/<int:post_id>/participate/', RequestPostParticipateView.as_view(),
                       name='api-post-participate'),
                  path('api/post/<int:post_id>/report/', PostReportView.as_view(), name='api-post-report'),
                  path('api/post/relatedto/', RelatedOptionList.as_view(), name='api-post-related-option-list'),
                  path('api/post/ngos/', NGOOptionList.as_view(), name='api-ngos-option-list'),

                  path('api/people/', PeopleList.as_view(), name='api-people-list'),
                  path('api/people/add/', PeopleAdd.as_view(), name='api-people-add'),
                  path('api/people/detail/', PeopleRUD.as_view(), name='api-people-detail'),
                  path('api/people/update/', PeopleRUD.as_view(), name='api-people-update'),
                  path('api/people/delete/', PeopleRUD.as_view(), name='api-people-delete'),
                  path('api/people/<int:pk>/', PeopleDetail.as_view(), name='api-people-detail'),

                  path('api/bank/<int:pk>/', BankDetail.as_view(), name='api-bank-detail'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
