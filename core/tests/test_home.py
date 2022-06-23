from django.urls import reverse

from core.tests.base import BaseTest


class AuthTest(BaseTest):

    def setUp(self):
        super().setUp()
        self.staff_home = reverse('staff-home')
        self.admin_home = reverse('admin-home')

    def test_admin_access_admin_home(self):
        self.login_as_admin()
        response = self.client.get(self.admin_home)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/admin/admin-home.html')

    def test_admin_access_staff_home(self):
        self.login_as_admin()
        response = self.client.get(self.staff_home)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/extensions/403-page.html')

    def test_staff_access_staff_home(self):
        self.login_as_staff()
        response = self.client.get(self.staff_home)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/staff/staff-home.html')

    def test_staff_access_admin_home(self):
        self.login_as_staff()
        response = self.client.get(self.admin_home)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/extensions/403-page.html')
