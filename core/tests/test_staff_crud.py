from django.urls import reverse

from core.enums import DBOperation
from core.models import Staff
from core.tests.base import BaseTest


def get_path(operation: DBOperation, pk: int):
    view_name = ''
    match operation:
        case DBOperation.read:
            view_name = 'read-staff'
        case DBOperation.update:
            view_name = 'update-staff'
        case DBOperation.delete:
            view_name = 'delete-staff'
    return reverse(view_name, kwargs={'pk': pk})


class StaffCRUDTest(BaseTest):

    def setUp(self):
        super().setUp()

        self.create_staff = reverse('create-staff')
        self.read_staffs = reverse('read-staffs')

        # img = BytesIO(b'core/static/core/img/website-logo.png')
        # img.name = 'website-logo.png'

        self.payload = {
            'username': 'staff2',
            'email': 'staff2@gmail.com',
            'password1': 'mango321',
            'password2': 'mango321',
            'full_name': 'staff2',
            'date_of_birth': '2001-10-25',
            'gender': 'Male',
            'phone': '9779800756475',
            'address': 'kalikanagar',
            'display_picture': '',
            'citizenship_photo': '',
            'is_married': False,
        }

    # ------------------------------------------------------------------------------------------------------------------

    def test_staff_access_create_staff_form(self):
        self.login_as_staff()
        response = self.client.get(self.create_staff)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/extensions/403-page.html')

    def test_staff_read_own_self(self):
        self.login_as_staff()
        response = self.client.get(get_path(DBOperation.read, 1))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/staff/staff-read.html')

    def test_staff_read_staffs(self):
        self.login_as_staff()
        response = self.client.get(self.read_staffs)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/extensions/403-page.html')

    def test_staff_access_update_staff_form(self):
        self.login_as_staff()
        response = self.client.get(get_path(DBOperation.update, 1))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/extensions/403-page.html')

    def test_staff_delete_staff(self):
        self.login_as_staff()
        response = self.client.delete(get_path(DBOperation.delete, 1))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/extensions/403-page.html')

    # ------------------------------------------------------------------------------------------------------------------

    def test_admin_access_create_staff_form(self):
        self.login_as_admin()
        response = self.client.get(self.create_staff)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/staff/staff-create.html')

    def test_admin_create_staff(self):
        self.login_as_admin()
        response = self.client.post(self.create_staff, self.payload, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Staff.objects.count(), 2)
        self.assertTrue(Staff.objects.filter(account__username=self.payload['username']))
        self.assertTemplateUsed(response, 'core/staff/staff-read.html')

    def test_admin_read_staff(self):
        self.login_as_admin()
        response = self.client.get(get_path(DBOperation.read, 1))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/staff/staff-read.html')

    def test_admin_read_staffs(self):
        self.login_as_admin()
        response = self.client.get(self.read_staffs)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/staff/staffs-read.html')

    def test_admin_access_update_staff_form(self):
        self.login_as_admin()
        response = self.client.get(get_path(DBOperation.update, 1))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/staff/staff-update.html')

    def test_admin_update_staff(self):
        self.login_as_admin()
        self.client.post(self.create_staff, self.payload, follow=True)
        old = Staff.objects.filter(account__username=self.payload['username']).first()
        self.payload['full_name'] = 'Mr XYZ'
        self.payload['is_married'] = True
        response = self.client.post(get_path(DBOperation.update, pk=old.pk), self.payload, follow=True)
        new = Staff.objects.filter(account__username=self.payload['username']).first()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(old.full_name != new.full_name)
        self.assertTrue(old.is_married != new.is_married)
        self.assertTemplateUsed(response, 'core/staff/staffs-read.html')

    def test_admin_delete_staff(self):
        self.login_as_admin()
        response = self.client.delete(get_path(DBOperation.delete, 1), follow=True)
        self.assertEqual(Staff.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/staff/staffs-read.html')
