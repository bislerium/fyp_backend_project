from rest_framework.authtoken.admin import User

from core.tests.base import BaseTest


class AuthTest(BaseTest):

    def setUp(self):
        super().setUp()

        self.wrong_user = {
            'username': 'whoami',
            'password': 'whoami',
        }

        self.ngo_user = {
            'username': 'ngo1',
            'password': 'mango321',
        }
        new_ngo = User.objects.create_user(**self.ngo_user)
        new_ngo.groups.add(self.ngo_group)
        new_ngo.save()

        self.general_user = {
            'username': 'general1',
            'password': 'mango321',
        }
        new_general = User.objects.create_user(**self.general_user)
        new_general.groups.add(self.general_group)
        new_general.save()

    def test_login_view_get_request(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/account/login.html')

    def test_can_admin_login(self):
        response = self.client.post(self.login_url, self.admin_user, follow=True)
        self.assertTrue(response.context['user'].is_active)

    def test_can_admin_logout(self):
        response = self.client.post(self.logout_url, follow=True)
        self.assertFalse(response.context['user'].is_active)

    def test_can_staff_login(self):
        response = self.client.post(self.login_url, self.staff_user, follow=True)
        self.assertTrue(response.context['user'].is_active)

    def test_can_staff_logout(self):
        response = self.client.post(self.logout_url, follow=True)
        self.assertFalse(response.context['user'].is_active)

    def test_can_general_login(self):
        response = self.client.post(self.login_url, self.general_user, follow=True)
        self.assertFalse(response.context['user'].is_active)

    def test_can_ngo_login(self):
        response = self.client.post(self.login_url, self.ngo_user, follow=True)
        self.assertFalse(response.context['user'].is_active)

    def test_can_un_authorize_login(self):
        response = self.client.post(self.login_url, self.wrong_user, follow=True)
        self.assertFalse(response.context['user'].is_active)

