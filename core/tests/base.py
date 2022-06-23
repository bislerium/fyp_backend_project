from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.urls import reverse

from core.models import Staff


class BaseTest(TestCase):

    def setUp(self):
        super().setUp()

        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

        self.general_group = Group.objects.create(name='General')
        self.ngo_group = Group.objects.create(name='NGO')
        self.staff_group = Group.objects.create(name='Staff')

        self.admin_user = {
            'username': 'admin',
            'password': 'admin',
        }
        User.objects.create_superuser(**self.admin_user)

        self.staff_user = {
            'username': 'staff1',
            'password': 'mango321',
        }
        self.new_staff = User.objects.create_user(**self.staff_user)
        Staff.objects.create(account=self.new_staff, full_name='staff1')
        self.new_staff.groups.add(self.staff_group)
        self.new_staff.save()

    def login_as_admin(self):
        return self.client.post(self.login_url, self.admin_user, follow=True)

    def login_as_staff(self):
        return self.client.post(self.login_url, self.staff_user, follow=True)
