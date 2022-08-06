import json
import os
from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DeleteView, UpdateView, DetailView, TemplateView, CreateView

from . import api_views
from .decorators import allowed_groups
from .fcm_notification import send_notification, ENotificationChannel
from .forms import *


def division(x, y):
    return x / y if y else 0


def ping_test(request):
    return HttpResponse(status=204)


def app_landing_page(request):
    section_a_app_image, section_b_app_image = get_section_images()
    return render(request, 'core/land/app-landing-page.html', context={
        'section_a_app_image': section_a_app_image,
        'section_b_app_image': section_b_app_image,
        'disable_footer': True,
        'disable_tooltip': True,
        'downlink_url': download_link['url'], })


def get_section_images():
    section_a_app_image = AppImage.objects.filter(image_section=IMAGE_SECTION[0][0])
    section_b_app_image = AppImage.objects.filter(image_section=IMAGE_SECTION[1][0])
    return section_a_app_image, section_b_app_image


def alp_setup(request):
    print('-------------')
    section_a_app_image, section_b_app_image = get_section_images()
    downlink = download_link['url'] if download_link['url'] else request.build_absolute_uri(reverse('coming-soon'))
    context = {
        'form1': ALPImageForm(),
        'form2': DownLinkForm(),
        'section_a_app_image': section_a_app_image,
        'section_b_app_image': section_b_app_image,
        'downlink_url':  downlink,
    }
    return render(request, 'core/land/page-setup.html', context)


def set_downlink_url(request):
    if request.method == 'POST':
        downlink_form = DownLinkForm(request.POST)
        if downlink_form.is_valid():
            print(downlink_form.data['downlink'])
            download_link['url'] = downlink_form.data['downlink']
            write_downlink()
    return redirect('alp-setup')


class ALPImageCreate(CreateView):
    model = AppImage
    form_class = ALPImageForm
    success_url = reverse_lazy('alp-setup')


class ALPImageDeleteView(DeleteView):
    model = AppImage
    success_url = reverse_lazy('alp-setup')


def coming_soon_page(request):
    return render(request, 'core/land/coming-soon.html', context={'disable_footer': True,
                                                                  'disable_bootstrap': True,
                                                                  'disable_tooltip': True})


def forbidden_page(request, exception):
    return render(request, 'core/extensions/403-page.html')


def page_not_found(request, exception):
    return render(request, 'core/extensions/404-page.html')


def bad_request(request, exception):
    return render(request, 'core/extensions/400-page.html')


def server_error(request, *args, **kwargs):
    return render(request, 'core/extensions/500-page.html')


class CustomWebLoginView(LoginView):

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_superuser and user.groups.first().name in ['General', 'NGO']:
            raise PermissionDenied
        return super().form_valid(form)


def home(request):
    if 'sessionid' in request.COOKIES.keys():
        return redirect('home-page-router')
    return redirect('app-landing-page')


@allowed_groups(admin=True, staff=True)
def home_page_router(request):
    user_: User = request.user
    if user_.is_staff and user_.is_superuser:
        return redirect('admin-home')
    if user_.groups.filter(name='Staff').exists():
        return redirect('staff-home')


@allowed_groups(admin=False, staff=True)
def staff_home(request):
    staff = request.user.staff
    context = {
        'staff_name': staff.full_name,
        'pending_reports': staff.report_review.filter(is_reviewed=False).count(),
        'reviewed_reports': staff.report_review.filter(is_reviewed=True).count(),
    }
    return render(request, 'core/staff/staff-home.html', context=context)


class AdminHome(TemplateView):
    template_name = 'core/admin/admin-home.html'

    @method_decorator(allowed_groups(admin=True, staff=False))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today_date: date = date.today()

        total_people = PeopleUser.objects.count()
        total_male_people = PeopleUser.objects.filter(gender='Male').count()
        total_female_people = PeopleUser.objects.filter(gender='Female').count()
        total_lgbtq_people = PeopleUser.objects.filter(gender='LGBTQ+').count()
        total_minor_people = PeopleUser.objects.filter(
            date_of_birth__gte=datetime(today_date.year - 18, today_date.month,
                                        today_date.day)).count()
        total_verified_people = PeopleUser.objects.filter(is_verified=True).count()
        total_active_people = PeopleUser.objects.filter(account__is_active=True).count()

        total_ngos = NGOUser.objects.count()
        total_verified_ngos = NGOUser.objects.filter(is_verified=True).count()
        total_active_ngos = NGOUser.objects.filter(account__is_active=True).count()
        ngos_per_field: dict = {}
        for fields in FIELD_OF_WORK:
            ngos_per_field[fields[0]] = NGOUser.objects.filter(field_of_work__contains=fields[0]).count()

        total_staffs = Staff.objects.count()
        total_married_staff = Staff.objects.filter(is_married=True).count()
        total_male_staff = Staff.objects.filter(gender='Male').count()
        total_female_staff = Staff.objects.filter(gender='Female').count()
        total_lgbtq_staff = Staff.objects.filter(gender='LGBTQ+').count()

        total_posts = Post.objects.all().count()
        total_normal_posts = PostNormal.objects.count()
        total_poll_posts = PostPoll.objects.count()
        total_request_posts = PostRequest.objects.count()
        total_join_request_posts = PostRequest.objects.filter(request_type='Join').count()
        total_petition_request_posts = PostRequest.objects.filter(request_type='Petition').count()
        total_removed_post = Post.objects.filter(is_removed=True).count()
        total_anonymous_post = Post.objects.filter(is_anonymous=True).count()
        total_post_normal_up_vote = 0
        total_post_normal_down_vote = 0
        total_reports = 0
        total_reported_posts = 0
        total_post_poll_options = PollOption.objects.count()
        total_post_poll_options_polled = 0
        total_post_request_petition_signed = 0
        total_post_request_join_signed = 0
        for normal_post in PostNormal.objects.all():
            total_post_normal_up_vote += normal_post.up_vote.count()
            total_post_normal_down_vote += normal_post.down_vote.count()
            report_count = normal_post.reported_by.count()
            total_reports += report_count
            if report_count != 0:
                total_reported_posts += 1
        for poll_post in PostPoll.objects.all():
            report_count = poll_post.reported_by.count()
            total_reports += report_count
            if report_count != 0:
                total_reported_posts += 1
        for poll_option in PollOption.objects.all():
            total_post_poll_options_polled += poll_option.reacted_by.count()
        for request_post in PostRequest.objects.all():
            report_count = request_post.reported_by.count()
            total_reports += report_count
            if report_count != 0:
                total_reported_posts += 1
            if request_post.request_type == 'Petition':
                total_post_request_petition_signed += request_post.reacted_by.count()
            if request_post.request_type == 'Join':
                total_post_request_join_signed += request_post.reacted_by.count()
        context['home'] = {
            'total_people': total_people,
            'total_male_people': total_male_people,
            'total_male_people_percentage': round(division(total_male_people, total_people) * 100, 2),
            'total_female_people': total_female_people,
            'total_female_people_percentage': round(division(total_female_people, total_people) * 100, 2),
            'total_lgbtq_people': total_lgbtq_people,
            'total_lgbtq_people_percentage': round(division(total_lgbtq_people, total_people) * 100, 2),
            'total_minor_people': total_minor_people,
            'total_minor_people_percentage': round(division(total_minor_people, total_people) * 100, 2),
            'total_verified_people': total_verified_people,
            'total_verified_people_percentage': round(division(total_verified_people, total_people) * 100, 2),
            'total_active_people': total_active_people,
            'total_active_people_percentage': round(division(total_active_people, total_people) * 100, 2),
            'total_ngos': total_ngos,
            'total_verified_ngos': total_verified_ngos,
            'total_verified_ngos_percentage': round(division(total_verified_ngos, total_ngos) * 100, 2),
            'total_active_ngos': total_active_ngos,
            'total_active_ngos_percentage': round(division(total_active_ngos, total_ngos) * 100, 2),
            'ngos_per_field': ngos_per_field,
            'total_staffs': total_staffs,
            'total_married_staff': total_married_staff,
            'total_married_staff_percentage': round(division(total_married_staff, total_staffs) * 100, 2),
            'total_male_staff': total_male_staff,
            'total_male_staff_percentage': round(division(total_male_staff, total_staffs) * 100, 2),
            'total_female_staff': total_female_staff,
            'total_female_staff_percentage': round(division(total_female_staff, total_staffs) * 100, 2),
            'total_lgbtq_staff': total_lgbtq_staff,
            'total_lgbtq_staff_percentage': round(division(total_lgbtq_staff, total_staffs) * 100, 2),
            'total_posts': total_posts,
            'total_normal_posts': total_normal_posts,
            'total_normal_posts_percentage': round(division(total_normal_posts, total_posts) * 100, 2),
            'total_poll_posts': total_poll_posts,
            'total_poll_posts_percentage': round(division(total_poll_posts, total_posts) * 100, 2),
            'total_request_posts': total_request_posts,
            'total_request_posts_percentage': round(division(total_request_posts, total_posts) * 100, 2),
            'total_join_request_posts': total_join_request_posts,
            'total_join_request_posts_percentage': round(division(total_join_request_posts, total_request_posts) * 100,
                                                         2),
            'total_petition_request_posts': total_petition_request_posts,
            'total_petition_request_posts_percentage': round(
                division(total_petition_request_posts, total_request_posts) * 100,
                2),
            'total_removed_post': total_removed_post,
            'total_removed_posts_percentage': round(division(total_removed_post, total_posts) * 100, 2),
            'total_anonymous_post': total_anonymous_post,
            'total_anonymous_posts_percentage': round(division(total_anonymous_post, total_posts) * 100, 2),
            'total_post_normal_up_vote': total_post_normal_up_vote,
            'avg_pn_up_vote_np': round(division(total_post_normal_up_vote, total_normal_posts)),
            'total_post_normal_down_vote': total_post_normal_down_vote,
            'avg_pn_down_vote_np': round(division(total_post_normal_down_vote, total_normal_posts)),
            'total_reports': total_reports,
            'total_reported_posts': total_reported_posts,
            'total_reports_percentage': round(division(total_reported_posts, total_posts) * 100, 2),
            'avg_reports_posts': round(division(total_reports, total_posts)),
            'total_post_poll_options': total_post_poll_options,
            'avg_pp_options_pp': round(division(total_post_poll_options, total_poll_posts)),
            'total_post_poll_options_polled': total_post_poll_options_polled,
            'avg_pp_options_polled_pp': round(division(total_post_poll_options_polled, total_post_poll_options)),
            'total_post_request_petition_signed': total_post_request_petition_signed,
            'avg_pr_petition_signed_rp': round(division(
                total_post_request_petition_signed, total_petition_request_posts)),
            'total_post_request_join_signed': total_post_request_join_signed,
            'avg_pr_join_signed_rp': round(
                division(total_post_request_join_signed, total_join_request_posts)),
        }
        return context


# Bank Crud

class BankCreate(CreateView):
    model = Bank
    form_class = BankCreationForm
    template_name = 'core/bank/bank-create.html'

    @method_decorator(allowed_groups(admin=True, staff=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @method_decorator(allowed_groups(admin=True, staff=True))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        ngo = get_object_or_404(NGOUser, pk=self.kwargs.get('pk'))
        ngo.bank = self.object
        ngo.save()
        return response

    def get_success_url(self):
        return reverse_lazy('read-ngo', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ngo_pk'] = self.kwargs['pk']
        return context


class BankUpdate(UpdateView):
    model = Bank
    form_class = BankCreationForm
    template_name = 'core/bank/bank-update.html'

    @method_decorator(allowed_groups(admin=True, staff=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @method_decorator(allowed_groups(admin=True, staff=True))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('read-ngo', kwargs={'pk': self.object.ngouser.id})


class BankDelete(DeleteView):
    model = Bank

    @method_decorator(allowed_groups(admin=True, staff=True))
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('read-ngo', kwargs={'pk': self.object.ngouser.id})


# Staff Crud

@allowed_groups(admin=True, )
def create_staff(request):
    user_form = CustomUserCreationForm()
    staff_form = StaffCreationForm()
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        staff_form = StaffCreationForm(request.POST, request.FILES or None)
        if user_form.is_valid() and staff_form.is_valid():
            user_form.save()
            user_account = User.objects.get(username=user_form.data['username'])
            user_account.groups.add(Group.objects.get(name='Staff'))
            user_account.save()
            staff = staff_form.save(commit=False)
            staff.account = user_account
            staff.save()
            api_views.staffs_deque.append(staff)
            messages.success(request, f'Account created for {staff_form.data["full_name"]}')
            return redirect('read-staff', staff.id)
    context = {
        'form1': user_form,
        'form2': staff_form,
    }
    return render(request, 'core/staff/staff-create.html', context)


class StaffsRead(ListView):
    paginate_by = 8
    template_name = 'core/staff/staffs-read.html'

    @method_decorator(allowed_groups(admin=True, staff=False))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Staff.objects.order_by('id')
        return get_filtered_queryset(self, queryset)


class StaffRead(DetailView):
    model = Staff
    template_name = 'core/staff/staff-read.html'

    @method_decorator(allowed_groups(admin=True, staff=True))
    def get(self, request, *args, **kwargs):
        staff: Staff = self.get_object()
        user: User = self.request.user
        if user.is_superuser or user == staff.account:
            return super().get(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.get('object').reviewed_posts = self.get_object().report_review.filter(is_reviewed=True).count()
        return context


class StaffUpdate(UpdateView):
    model = Staff
    form_class = StaffCreationForm
    template_name = 'core/staff/staff-update.html'
    success_url = reverse_lazy('read-staffs')

    def form_valid(self, form):
        if not form.instance.display_picture:
            form.instance.display_picture = settings.DEFAULT_PEOPLE_DP
        return super().form_valid(form)

    @method_decorator(allowed_groups(admin=True, staff=False))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @method_decorator(allowed_groups(admin=True, staff=False))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class StaffDelete(DeleteView):
    model = Staff
    success_url = reverse_lazy('read-staffs')

    @method_decorator(allowed_groups(admin=True, staff=False))
    def delete(self, request, *args, **kwargs):
        api_views.staffs_deque.remove(self.get_object())
        return super().delete(request, *args, **kwargs)


# People CRUD

class PeoplesRead(ListView):
    paginate_by = 8
    template_name = 'core/general/peoples-read.html'

    @method_decorator(allowed_groups(admin=True, staff=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = PeopleUser.objects.order_by('id')
        return get_filtered_queryset(self, queryset)


class PeopleRead(DetailView):
    model = PeopleUser
    template_name = 'core/general/people-read.html'

    @method_decorator(allowed_groups(admin=True, staff=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PeopleUpdate(UpdateView):
    model = PeopleUser
    form_class = PeopleCreationForm
    template_name = 'core/general/people-update.html'
    success_url = reverse_lazy('read-peoples')

    @method_decorator(allowed_groups(admin=True, staff=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @method_decorator(allowed_groups(admin=True, staff=True))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        if not form.instance.display_picture:
            form.instance.display_picture = settings.DEFAULT_PEOPLE_DP
        new = form.instance.is_verified
        old = PeopleUser.objects.get(pk=self.object.pk).is_verified
        if new and new != old:
            send_verify_notification(self.object.account.id)
        return super().form_valid(form)


class PeopleDelete(DeleteView):
    model = PeopleUser
    success_url = reverse_lazy('read-peoples')

    @method_decorator(allowed_groups(admin=True, staff=True))
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


# NGO Crud
@allowed_groups(admin=True, staff=True)
def create_ngo(request):
    user_form = CustomUserCreationForm()
    ngo_form = NGOCreationForm()
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        ngo_form = NGOCreationForm(request.POST, request.FILES or None)
        if user_form.is_valid() and ngo_form.is_valid():
            user_form.save()
            user_account = User.objects.get(username=user_form.data['username'])
            user_account.groups.add(Group.objects.get(name='NGO'))
            user_account.save()
            ngo = ngo_form.save(commit=False)
            ngo.account = user_account
            ngo.save()
            messages.success(request, f'Account created for {ngo_form.data["full_name"]}')
            if not ngo.is_verified:
                return redirect('read-ngo', ngo.id)
            return redirect('create-bank', ngo.id)
    context = {
        'form1': user_form,
        'form2': ngo_form,
    }
    return render(request, 'core/ngo/ngo-create.html', context)


class NGOsRead(ListView):
    paginate_by = 8
    template_name = 'core/ngo/ngos-read.html'

    @method_decorator(allowed_groups(admin=True, staff=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = NGOUser.objects.order_by('id')
        return get_filtered_queryset(self, queryset)


def get_filtered_queryset(self, queryset):
    query_params = self.request.GET
    if query_params and 'name' in query_params.keys() and 'filter_by' in query_params.keys():
        if query_params['filter_by'] == 'username':
            queryset = queryset.filter(account__username__icontains=query_params['name'])
        if query_params['filter_by'] == 'fullname':
            queryset = queryset.filter(full_name__icontains=query_params['name'])
    return queryset


class NGORead(DetailView):
    model = NGOUser
    template_name = 'core/ngo/ngo-read.html'

    @method_decorator(allowed_groups(admin=True, staff=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class NGOUpdate(UpdateView):
    model = NGOUser
    form_class = NGOCreationForm
    template_name = 'core/ngo/ngo-update.html'
    success_url = reverse_lazy('read-ngos')

    @method_decorator(allowed_groups(admin=True, staff=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @method_decorator(allowed_groups(admin=True, staff=True))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        if not form.instance.display_picture:
            form.instance.display_picture = settings.DEFAULT_NGO_DP
        new = form.instance.is_verified
        old = NGOUser.objects.get(pk=self.object.pk).is_verified
        if new and new != old:
            send_verify_notification(self.object.account.id)
        return super().form_valid(form)


def send_verify_notification(account_id: int):
    send_notification(title=f'Account Verification',
                      body=f'Your account has been verified.\nPlease support the community and'
                           f' follow the guidelines.\nKeep Sasae a better place for social enthusiasts. ❤',
                      notification_for=account_id,
                      channel=ENotificationChannel['verify'],
                      post_type=None, post_id=None)


class NGODelete(DeleteView):
    model = NGOUser
    success_url = reverse_lazy('read-ngos')

    @method_decorator(allowed_groups(admin=True, staff=True))
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class ReportRead(DetailView):
    model = Post
    template_name = 'core/report/report-review-read.html'

    @method_decorator(allowed_groups(admin=True, staff=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post: Post = context.get('object')
        report_form = ReportForm(instance=Report.objects.get(post=post))
        if post.post_type == 'Poll':
            cont: list = []
            total_reaction = 0
            for option in post.postpoll.option.all():
                total_reaction += option.reacted_by.count()
            for option in post.postpoll.option.all():
                reaction = option.reacted_by.count()
                percentage = division(reaction, total_reaction) * 100
                cont.append((option.option, reaction, round(percentage)))
            context['object'].poll_data = cont
            context['object'].poll_reactions = total_reaction
        if post.post_type == 'Request':
            min_ = post.postrequest.min
            target = post.postrequest.target
            max_ = post.postrequest.max
            sign = post.postrequest.reacted_by.count()
            cont: dict = {'min_': min_,
                          'target': target,
                          'sign': sign,
                          'target_percentage': 100,
                          'min_percentage': round((division(100, target)) * min_, 2),
                          'sign_percentage': round(division(100, target) * sign, 2),
                          }
            if max_ is not None:
                cont['max_'] = max_
                cont['max_percentage'] = 100
                cont['target_percentage'] = round(division(100, max_) * target, 2)
                cont['min_percentage'] = round(division(100, max_) * min_, 2)
                cont['sign_percentage'] = round(division(100, max_) * sign, 2)
            context['object'].request_data = cont
        context['object'].report_form = report_form
        return context


class ReportsRead(ListView):
    model = Post
    template_name = 'core/report/reports-read.html'

    @method_decorator(allowed_groups(admin=True, staff=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        if self.request.user.is_superuser:
            reviewed_reports = Report.objects.filter(is_reviewed=True)
            context['object_list'] = [report.post for report in reviewed_reports]
            context['post_reviewed'] = reviewed_reports.count()
            context['total_reports'] = Report.objects.count()
        else:
            staff: Staff = Staff.objects.get(account=self.request.user)
            reviewed_reports = staff.report_review.filter(is_reviewed=False)
            total_reports = staff.report_review.count()
            context['object_list'] = [report.post for report in reviewed_reports]
            context['post_reviewed'] = total_reports - reviewed_reports.count()
            context['total_reports'] = total_reports
        return context


class ReportUpdate(UpdateView):
    model = Report
    form_class = ReportForm
    success_url = reverse_lazy('read-reports')

    @method_decorator(allowed_groups(admin=False, staff=True))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == 'get':
            return self.http_method_not_allowed(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        report = self.get_object()
        post = report.post

        action_option = form.data['action']
        reason = form.data['reason']
        report.is_reviewed = True
        report.action = action_option
        report.reason = reason
        report.save()

        people: PeopleUser = post.people_posted_post_rn.first()
        ngo: NGOUser = post.ngo_posted_post_rn.first()

        if action_option == Report.ACTION[0][0]:
            post.is_removed = True
            post.save()

            send_notification(title=f'{post.post_type} Post Removed',
                              body=f'Your Post has been removed. The action was made upon close '
                                   f'inspection of your post content after getting multiple general reports.\n\n'
                                   f'[REASON]\n{reason}',
                              notification_for=(people or ngo).account.id,
                              channel=ENotificationChannel['remove'],
                              post_type=None, post_id=None)

        if action_option == Report.ACTION[1][0]:
            if people is not None:
                account = people.account
                account.is_active = False
                account.save()
            if ngo is not None:
                account = ngo.account
                account.is_active = False
                account.save()
        return HttpResponseRedirect(self.get_success_url())


@allowed_groups(admin=True, staff=True)
def set_profile_active(request, user_type, pk, action):
    match user_type:
        case 'people':
            people_user: PeopleUser = get_object_or_404(PeopleUser, id=pk)
            match action:
                case 'verify':
                    people_user.is_verified = True
                    people_user.save()
                    send_verify_notification(people_user.account.id)
                case 'active':
                    people_user.account.is_active = True
                    people_user.account.save()
            return redirect('read-people', pk=pk)
        case 'ngo':
            ngo_user: NGOUser = get_object_or_404(NGOUser, id=pk)
            match action:
                case 'verify':
                    ngo_user.is_verified = True
                    ngo_user.save()
                    send_verify_notification(ngo_user.account.id)
                case 'active':
                    ngo_user.account.is_active = True
                    ngo_user.account.save()
            return redirect('read-ngo', pk=pk)


@allowed_groups(admin=True, staff=False)
def toggle_staff_active(request, pk):
    user: User = get_object_or_404(Staff, id=pk).account
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()
    return redirect('read-staff', pk=pk)


download_link = {'url': None}
downlink_filename = 'app_downlink.json'


def write_downlink():
    with open(downlink_filename, "w") as outfile:
        json.dump(download_link, outfile)


def read_downlink():
    if os.path.exists(downlink_filename):
        with open(downlink_filename, 'r') as openfile:
            json_object = json.load(openfile)


read_downlink()
