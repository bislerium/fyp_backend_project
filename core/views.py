from typing import Union

from datetime import date, datetime
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, UpdateView, DetailView, TemplateView

from .forms import *


def redirection(request, **kwargs: Union[reverse_lazy, redirect]):
    print("hellothere")
    user_: User = request.user
    print(user_.groups)
    if user_.is_staff and user_.is_superuser:
        print('a')
        return kwargs['admin_redirect']
    if user_.groups.filter(name=Group.objects.get(name__iexact='Staff')).exists():
        print('b')
        return kwargs['staff_redirect']
    if user_.groups.filter(name=Group.objects.get(name__iexact='People')).exists() or \
            user_.groups.filter(name=Group.objects.get(name__iexact='NGO')).exists():
        print('c')
        return kwargs['user_redirect']


def forbidden_page(request):
    return render(request, 'core/extensions/403-page.html')


def page_not_found(request):
    return render(request, 'core/extensions/404-page.html')


def home_page(request):
    return redirection(request,
                       admin_redirect=redirect('admin-home'),
                       staff_redirect=redirect('read-reports'),
                       user_redirect=redirect('forbid'))


# Create your views here.

class CustomLoginView(LoginView):

    def get_success_url(self):
        return redirection(self.request,
                           admin_redirect=reverse_lazy('admin-home'),
                           staff_redirect=reverse_lazy('read-reports'),
                           user_redirect=reverse_lazy('forbid'))


def staff_index(request):
    return render(request, 'core/staff/staff-reported-post-review.html', context={'pk': request.user.username})


# Staff Crud

def create_staff(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        staff_form = StaffCreationForm(request.POST, request.FILES or None)
        if user_form.is_valid() and staff_form.is_valid():
            user_form.save()
            staff_form_ = staff_form.save(commit=False)
            staff_form_.account = User.objects.get(username=user_form.data['username'])
            staff_form_.save()
            messages.success(request, f'Account created for {staff_form.data["full_name"]}')
            return redirect('read-staffs')
    context = {
        'form1': UserCreationForm(),
        'form2': PeopleCreationForm(),
    }
    return render(request, 'core/staff/staff-create.html', context)


class read_staffs(ListView):
    model = Staff
    # paginate_by = 20
    template_name = 'core/staff/staffs-read.html'


class read_staff(DetailView):
    model = Staff
    template_name = 'core/staff/staff-read.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.get('object').reviewed_posts = self.get_object().report_review.filter(review=True).count()
        return context


class update_staff(UpdateView):
    model = Staff
    form_class = StaffCreationForm
    template_name = 'core/staff/staff-update.html'
    success_url = reverse_lazy('read-staffs')


class delete_staff(DeleteView):
    model = Staff
    success_url = reverse_lazy('read-staffs')


# People CRUD

class read_peoples(ListView):
    model = PeopleUser
    # paginate_by = 20
    template_name = 'core/user/peoples-read.html'


class read_people(DetailView):
    model = PeopleUser
    template_name = 'core/user/people-read.html'


class update_people(UpdateView):
    model = PeopleUser
    form_class = PeopleCreationForm
    template_name = 'core/user/people-update.html'
    success_url = reverse_lazy('read-peoples')


class delete_people(DeleteView):
    model = PeopleUser
    success_url = reverse_lazy('read-peoples')


# NGO Crud

def create_ngo(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        ngo_form = NGOCreationForm(request.POST, request.FILES or None)
        if user_form.is_valid() and ngo_form.is_valid():
            user_form.save()
            ngo_form_ = ngo_form.save(commit=False)
            ngo_form_.account = User.objects.get(username=user_form.data['username'])
            ngo_form_.save()
            messages.success(request, f'Account created for {ngo_form.data["full_name"]}')
            return redirect('read-ngos')
    context = {
        'form1': UserCreationForm(),
        'form2': NGOCreationForm(),
    }
    return render(request, 'core/ngo/ngo-create.html', context)


class read_ngos(ListView):
    model = NGOUser
    # paginate_by = 20
    template_name = 'core/ngo/ngos-read.html'


class read_ngo(DetailView):
    model = NGOUser
    template_name = 'core/ngo/ngo-read.html'


class update_ngo(UpdateView):
    model = NGOUser
    form_class = NGOCreationForm
    template_name = 'core/ngo/ngo-update.html'
    success_url = reverse_lazy('read-ngos')


class delete_ngo(DeleteView):
    model = NGOUser
    success_url = reverse_lazy('read-ngos')


class read_report(DetailView):
    model = Post
    template_name = 'core/staff/staff-reported-post-review.html'

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
                percentage = (reaction / total_reaction) * 100
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
                          'min_percentage': round((100 / target) * min_, 2),
                          'sign_percentage': round((100 / target) * sign, 2),
                          }
            if max_ is not None:
                cont['max_'] = max_
                cont['max_percentage'] = 100
                cont['target_percentage'] = round((100 / max_) * target, 2)
                cont['min_percentage'] = round((100 / max_) * min_, 2)
                cont['sign_percentage'] = round((100 / max_) * sign, 2)
            context['object'].request_data = cont
        context['object'].report_form = report_form
        return context


class read_reports(ListView):
    model = Post
    template_name = 'core/staff/staff-home-reported-post.html'


class update_report(UpdateView):
    model = Report
    form_class = ReportForm
    success_url = reverse_lazy('read-reports')

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == 'get':
            return self.http_method_not_allowed(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        return super().form_valid(form)


class admin_home(TemplateView):
    template_name = 'core/admin/admin-home.html'

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
        total_verified_people = PeopleUser.objects.filter(verified=True).count()
        total_active_people = PeopleUser.objects.filter(account__is_active=True).count()

        total_ngos = NGOUser.objects.count()
        total_verified_ngos = NGOUser.objects.filter(verified=True).count()
        total_active_ngos = NGOUser.objects.filter(account__is_active=True).count()
        ngos_per_field: dict = {}
        for fields in FIELD_OF_WORK:
            ngos_per_field[fields[0]] = NGOUser.objects.filter(field_of_work__contains=fields[0]).count()

        total_staffs = Staff.objects.count()
        total_married_staff = Staff.objects.filter(marital_status=True).count()
        total_male_staff = Staff.objects.filter(gender='Male').count()
        total_female_staff = Staff.objects.filter(gender='Female').count()
        total_lgbtq_staff = Staff.objects.filter(gender='LGBTQ+').count()

        total_posts = Post.objects.all().count()
        total_normal_posts = PostNormal.objects.count()
        total_poll_posts = PostPoll.objects.count()
        total_request_posts = PostRequest.objects.count()
        total_join_request_posts = PostRequest.objects.filter(request_type='Join').count()
        total_petition_request_posts = PostRequest.objects.filter(request_type='Petition').count()
        total_removed_post = Post.objects.filter(removed=True).count()
        total_anonymous_post = Post.objects.filter(anonymous=True).count()
        total_post_normal_up_vote = 0
        total_post_normal_down_vote = 0
        total_reports = 0
        total_post_poll_options = PollOption.objects.count()
        total_post_poll_options_polled = 0
        total_post_request_petition_signed = 0
        total_post_request_join_signed = 0
        for normal_post in PostNormal.objects.all():
            total_post_normal_up_vote += normal_post.up_vote.count()
            total_post_normal_down_vote += normal_post.down_vote.count()
            total_reports += normal_post.reported_by.count()
        for poll_post in PostPoll.objects.all():
            total_reports += poll_post.reported_by.count()
        for poll_option in PollOption.objects.all():
            total_post_poll_options_polled += poll_option.reacted_by.count()
        for request_post in PostRequest.objects.all():
            total_reports += request_post.reported_by.count()
            if request_post.request_type == 'Petition':
                total_post_request_petition_signed += request_post.reacted_by.count()
            if request_post.request_type == 'Join':
                total_post_request_join_signed += request_post.reacted_by.count()
        context['home'] = {
            'total_people': total_people,
            'total_male_people': total_male_people,
            'total_male_people_percentage': round((total_male_people / total_people) * 100, 2),
            'total_female_people': total_female_people,
            'total_female_people_percentage': round((total_female_people / total_people) * 100, 2),
            'total_lgbtq_people': total_lgbtq_people,
            'total_lgbtq_people_percentage': round((total_lgbtq_people / total_people) * 100, 2),
            'total_minor_people': total_minor_people,
            'total_minor_people_percentage': round((total_minor_people / total_people) * 100, 2),
            'total_verified_people': total_verified_people,
            'total_verified_people_percentage': round((total_verified_people / total_people) * 100, 2),
            'total_active_people': total_active_people,
            'total_active_people_percentage': round((total_active_people / total_people) * 100, 2),
            'total_ngos': total_ngos,
            'total_verified_ngos': total_verified_ngos,
            'total_verified_ngos_percentage': round((total_verified_ngos / total_people) * 100, 2),
            'total_active_ngos': total_active_ngos,
            'total_active_ngos_percentage': round((total_active_ngos / total_people) * 100, 2),
            'ngos_per_field': ngos_per_field,
            'total_staffs': total_staffs,
            'total_married_staff': total_married_staff,
            'total_married_staff_percentage': round((total_married_staff / total_staffs) * 100, 2),
            'total_male_staff': total_male_staff,
            'total_male_staff_percentage': round((total_male_staff / total_staffs) * 100, 2),
            'total_female_staff': total_female_staff,
            'total_female_staff_percentage': round((total_female_staff / total_staffs) * 100, 2),
            'total_lgbtq_staff': total_lgbtq_staff,
            'total_lgbtq_staff_percentage': round((total_lgbtq_staff / total_staffs) * 100, 2),
            'total_posts': total_posts,
            'total_normal_posts': total_normal_posts,
            'total_normal_posts_percentage': round((total_normal_posts / total_posts) * 100, 2),
            'total_poll_posts': total_poll_posts,
            'total_poll_posts_percentage': round((total_poll_posts / total_posts) * 100, 2),
            'total_request_posts': total_request_posts,
            'total_request_posts_percentage': round((total_request_posts / total_posts) * 100, 2),
            'total_join_request_posts': total_join_request_posts,
            'total_join_request_posts_percentage': round((total_join_request_posts / total_request_posts) * 100, 2),
            'total_petition_request_posts': total_petition_request_posts,
            'total_petition_request_posts_percentage': round((total_petition_request_posts / total_request_posts) * 100, 2),
            'total_removed_post': total_removed_post,
            'total_removed_posts_percentage': round((total_removed_post / total_posts) * 100, 2),
            'total_anonymous_post': total_anonymous_post,
            'total_anonymous_posts_percentage': round((total_anonymous_post / total_posts) * 100, 2),
            'total_post_normal_up_vote': total_post_normal_up_vote,
            'avg_pn_up_vote_np': round(total_post_normal_up_vote / total_normal_posts),
            'total_post_normal_down_vote': total_post_normal_down_vote,
            'avg_pn_down_vote_np': round(total_post_normal_down_vote / total_normal_posts),
            'total_reports': total_reports,
            'avg_reports_posts': round(total_reports / total_posts),
            'total_post_poll_options': total_post_poll_options,
            'avg_pp_options_pp': round(total_post_poll_options / total_poll_posts),
            'total_post_poll_options_polled': total_post_poll_options_polled,
            'avg_pp_options_polled_pp': round(total_post_poll_options_polled / total_post_poll_options),
            'total_post_request_petition_signed': total_post_request_petition_signed,
            'avg_pr_petition_signed_rp': round(
                total_post_request_petition_signed / total_petition_request_posts),
            'total_post_request_join_signed': total_post_request_join_signed,
            'avg_pr_join_signed_rp': round(
                total_post_request_join_signed / total_join_request_posts),
        }
        print(context['home'])
        return context
