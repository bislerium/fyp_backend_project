from django.contrib.auth.models import User
from django.urls import reverse

from core.models import PeopleUser, Post, PostNormal, Report
from core.tests.base import BaseTest


class PostReportReviewTest(BaseTest):

    def setUp(self):
        super().setUp()

        self.read_reports = reverse('read-reports')

        self.payload = {
            'reason': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam aliquam, ipsum efficitur '
                      'ultricies dapibus, tortor mi rhoncus nisi, sit amet vehicula justo arcu eget massa. Proin '
                      'libero sapien, dignissim ut malesuada at, lobortis quis lacus. Sed ornare mauris ac leo '
                      'rhoncus vestibulum. Praesent lacus purus, sollicitudin vel velit sagittis, volutpat varius '
                      'tortor. Nulla non fermentum sapien. Nam sed fermentum neque. Nunc aliquet lacinia ornare.',
            'action': 'Account Ban',
        }
        user = User.objects.create_user(username='people1', password='mango321')
        self.people = PeopleUser.objects.create(account=user, full_name='mr xyz', phone='9779800730959')
        post = Post.objects.create(related_to=['Communication', 'Labor'], post_content='lorem epsum',
                                   post_type='Normal')
        normal_post = PostNormal.objects.create(post=post, )
        normal_post.reported_by.add(self.people)
        self.people.posted_post.add(post)
        self.report = Report.objects.create(post=post)
        self.new_staff.staff.report_review.add(self.report)

    # ------------------------------------------------------------------------------------------------------------------

    def test_admin_access_reports(self):
        self.login_as_admin()
        response = self.client.get(self.read_reports)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/report/reports-read.html')

    def test_staff_access_reports(self):
        self.login_as_staff()
        response = self.client.get(self.read_reports)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/report/reports-read.html')

    def test_admin_read_report(self):
        self.login_as_admin()
        response = self.client.get(reverse('read-report', kwargs={'pk': self.report.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/report/report-review-read.html')

    def test_staff_read_report(self):
        self.login_as_staff()
        response = self.client.get(reverse('read-report', kwargs={'pk': self.report.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/report/report-review-read.html')

    def test_admin_review_report(self):
        self.login_as_admin()
        response = self.client.post(reverse('review-report', kwargs={'pk': self.report.id}), data=self.payload)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/extensions/403-page.html')

    def test_staff_review_report(self):
        self.login_as_staff()
        response = self.client.post(reverse('review-report', kwargs={'pk': self.report.id}), data=self.payload,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        new = Report.objects.get(pk=self.report.id)
        self.assertEqual(new.is_reviewed, True)
        self.assertEqual(new.reason, self.payload['reason'])
        self.assertEqual(new.action, self.payload['action'])
        if self.payload['action'] == Report.ACTION[0][0]:
            self.assertEqual(new.post.is_removed, True)
        if self.payload['action'] == Report.ACTION[1][0]:
            self.assertEqual((new.post.people_posted_post_rn or new.post.ngo_posted_post_rn).first().account.is_active,
                             False)
        self.assertTemplateUsed(response, 'core/report/reports-read.html')
