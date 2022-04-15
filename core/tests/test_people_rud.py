from django.contrib.auth.models import User
from django.urls import reverse

from core.enums import DBOperation
from core.models import PeopleUser
from core.tests.base import BaseTest


def get_path(operation: DBOperation, pk: int):
    view_name = ''
    match operation:
        case DBOperation.read:
            view_name = 'read-people'
        case DBOperation.update:
            view_name = 'update-people'
        case DBOperation.delete:
            view_name = 'delete-people'
    return reverse(view_name, kwargs={'pk': pk})


class PeopleCRUDTest(BaseTest):

    def setUp(self):
        super().setUp()

        self.read_peoples = reverse('read-peoples')

        user = User.objects.create_user(username='people1', password='mango321')
        self.payload = {
            'account': user,
            'full_name': 'Mrs XYZ',
            'date_of_birth': '2002-11-14',
            'gender': 'Female',
            'phone': '9779844657384',
            'address': 'Lalitpur',
            'display_picture': '',
            'citizenship_photo': '',
            'is_verified': False
        }

        self.people = PeopleUser.objects.create(**self.payload)

    # ------------------------------------------------------------------------------------------------------------------

    def test_staff_read_people(self):
        self.login_as_staff()
        response = self.client.get(get_path(DBOperation.read, self.people.pk))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/user/people-read.html')

    def test_staff_read_peoples(self):
        self.login_as_staff()
        response = self.client.get(self.read_peoples)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/user/peoples-read.html')

    def test_staff_access_update_people_form(self):
        self.login_as_staff()
        response = self.client.get(get_path(DBOperation.update, self.people.pk))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/user/people-update.html')

    def test_staff_update_people(self):
        self.login_as_staff()
        self.payload.pop('account')
        self.payload['address'] = 'Bhaktapur'
        self.payload['is_verified'] = True
        response = self.client.post(get_path(DBOperation.update, pk=self.people.pk), self.payload, follow=True)
        new = PeopleUser.objects.filter(pk=self.people.pk).first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(new.address, self.payload['address'])
        self.assertEqual(new.is_verified, self.payload['is_verified'])
        self.assertTemplateUsed(response, 'core/user/peoples-read.html')

    def test_staff_delete_people(self):
        self.login_as_staff()
        response = self.client.delete(get_path(DBOperation.delete, pk=self.people.pk), follow=True)
        self.assertEqual(PeopleUser.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/user/peoples-read.html')
