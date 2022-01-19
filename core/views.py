from datetime import date, datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, UpdateView, DetailView, TemplateView, CreateView

from .decorators import allowed_groups
from .forms import *


def division(x, y):
    return x / y if y else 0


def forbidden_page(request, exception):
    print(exception)
    return render(request, 'core/extensions/403-page.html')


def page_not_found(request, exception):
    print(exception)
    return render(request, 'core/extensions/404-page.html')


def bad_request(request, exception):
    print(exception)
    return render(request, 'core/extensions/400-page.html')


def home_page(request):
    user_: User = request.user
    if user_.is_staff and user_.is_superuser:
        print('admin')
        return redirect('admin-home')
    if user_.groups.filter(name='Staff').exists():
        print('wow')
        return redirect('staff-home')
    if user_.groups.filter(name__in=['People', 'NGO']).exists():
        print('Hello')
        raise PermissionDenied(f'{user_} is not identified, falls under {user_.groups.first()}!')


# Create your views here.

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
        print(context['home'])
        return context


# Bank Crud

class create_bank(CreateView):
    model = Bank
    form_class = BankCreationForm
    template_name = 'core/bank/bank-create.html'

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


class update_bank(UpdateView):
    model = Bank
    form_class = BankCreationForm
    template_name = 'core/bank/bank-update.html'

    def get_success_url(self):
        return reverse_lazy('read-ngo', kwargs={'pk': self.object.ngouser.id})


class delete_bank(DeleteView):
    model = Bank

    def get_success_url(self):
        return reverse_lazy('read-ngo', kwargs={'pk': self.object.ngouser.id})


# Staff Crud

def staff_home(request):
    return render(request, 'core/staff/staff-home.html')


@login_required(login_url=reverse_lazy('login'))
@allowed_groups('Staff', 'Admin')
def create_staff(request):
    user_form = UserCreationForm()
    staff_form = StaffCreationForm()
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        staff_form = StaffCreationForm(request.POST, request.FILES or None)
        if user_form.is_valid() and staff_form.is_valid():
            user_form.save()
            user_account = User.objects.get(username=user_form.data['username'])
            user_account.groups.add(Group.objects.get(name='Staff'))
            user_account.save()
            staff = staff_form.save(commit=False)
            staff.account = user_account
            staff.save()
            messages.success(request, f'Account created for {staff_form.data["full_name"]}')
            return redirect('read-staff', staff.id)
    context = {
        'form1': user_form,
        'form2': staff_form,
    }
    return render(request, 'core/staff/staff-create.html', context)


class read_staffs(PermissionRequiredMixin, ListView):
    permission_required = 'core.view_staff'
    model = Staff
    # paginate_by = 20
    template_name = 'core/staff/staffs-read.html'


class read_staff(DetailView):
    model = Staff
    template_name = 'core/staff/staff-read.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.get('object').reviewed_posts = self.get_object().report_review.filter(is_reviewed=True).count()
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
    user_form = UserCreationForm()
    ngo_form = NGOCreationForm()
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
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
            return redirect('create-bank', ngo.id)
    context = {
        'form1': user_form,
        'form2': ngo_form,
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
    template_name = 'core/report/report-review-read.html'

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
            print(cont)
            if max_ is not None:
                cont['max_'] = max_
                cont['max_percentage'] = 100
                cont['target_percentage'] = round(division(100, max_) * target, 2)
                cont['min_percentage'] = round(division(100, max_) * min_, 2)
                cont['sign_percentage'] = round(division(100, max_) * sign, 2)
            context['object'].request_data = cont
        context['object'].report_form = report_form
        return context


class read_reports(ListView):
    model = Post
    template_name = 'core/report/reports-read.html'

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


class update_report(UpdateView):
    model = Report
    form_class = ReportForm
    success_url = reverse_lazy('read-reports')

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == 'get':
            return self.http_method_not_allowed(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        action_option = form['action'].data
        post = form.instance.post
        form.instance.is_reviewed = True
        if action_option == Report.ACTION[0][0]:
            post.is_removed = True
            post.save()
        if action_option == Report.ACTION[1][0]:
            people: PeopleUser = post.people_posted_post_rn.first()
            ngo: NGOUser = post.ngo_posted_post_rn.first()
            if people is not None:
                account = people.account
                account.is_active = False
                account.save()
            if ngo is not None:
                account = ngo.account
                account.is_active = False
                account.save()
        return super().form_valid(form)
