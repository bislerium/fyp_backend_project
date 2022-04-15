from django.urls import reverse

from core.enums import DBOperation
from core.models import NGOUser
from core.tests.base import BaseTest


def get_path(operation: DBOperation, pk: int):
    view_name = ''
    match operation:
        case DBOperation.read:
            view_name = 'read-ngo'
        case DBOperation.update:
            view_name = 'update-ngo'
        case DBOperation.delete:
            view_name = 'delete-ngo'
    return reverse(view_name, kwargs={'pk': pk})


class NGOCRUDTest(BaseTest):

    def setUp(self):
        super().setUp()

        self.create_ngo = reverse('create-ngo')
        self.read_ngos = reverse('read-ngos')

        self.payload = {
            'username': 'ngo1',
            'email': 'ngo1@gmail.com',
            'password1': 'mango321',
            'password2': 'mango321',
            'full_name': 'Nepal NGO Federation',
            'establishment_date': '2012-10-25',
            'field_of_work': ['Communication', 'Education'],
            'phone': '9779844563748',
            'address': 'Kathmandu',
            'latitude': 82.123,
            'longitude': 120.232,
            'display_picture': '',
            'epay_account': '9844563748',
            'swc_affl_cert': '',
            'pan_cert': '',
            'is_verified': False,
        }

    # ------------------------------------------------------------------------------------------------------------------

    def test_staff_access_create_ngo_form(self):
        self.login_as_staff()
        response = self.client.get(self.create_ngo)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/ngo/ngo-create.html')

    def test_staff_create_ngo(self):
        self.login_as_staff()
        response = self.client.post(self.create_ngo, self.payload, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(NGOUser.objects.count(), 1)
        self.assertTrue(NGOUser.objects.filter(account__username=self.payload['username']))
        self.assertTemplateUsed(response, 'core/ngo/ngo-read.html')

    def test_staff_read_ngo(self):
        self.login_as_staff()
        self.client.post(self.create_ngo, self.payload, follow=True)
        ngo = NGOUser.objects.all().first()
        response = self.client.get(get_path(DBOperation.read, ngo.pk))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/ngo/ngo-read.html')

    def test_staff_read_ngos(self):
        self.login_as_staff()
        response = self.client.get(self.read_ngos)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/ngo/ngos-read.html')

    def test_staff_access_update_ngo_form(self):
        self.login_as_staff()
        self.client.post(self.create_ngo, self.payload, follow=True)
        ngo = NGOUser.objects.all().first()
        response = self.client.get(get_path(DBOperation.update, ngo.pk))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/ngo/ngo-update.html')

    def test_staff_update_ngo(self):
        self.login_as_staff()
        self.client.post(self.create_ngo, self.payload, follow=True)
        old = NGOUser.objects.filter(account__username=self.payload['username']).first()
        self.payload['full_name'] = 'XYZ Company'
        self.payload['phone'] = '9779856475894'
        response = self.client.post(get_path(DBOperation.update, pk=old.pk), self.payload, follow=True)
        new = NGOUser.objects.filter(account__username=self.payload['username']).first()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(old.full_name != new.full_name)
        self.assertTrue(old.phone != new.phone)
        self.assertTemplateUsed(response, 'core/ngo/ngos-read.html')

    def test_staff_delete_ngo(self):
        self.login_as_staff()
        self.client.post(self.create_ngo, self.payload, follow=True)
        ngo = NGOUser.objects.all().first()
        response = self.client.delete(get_path(DBOperation.delete, pk=ngo.pk), follow=True)
        self.assertEqual(NGOUser.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/ngo/ngos-read.html')
