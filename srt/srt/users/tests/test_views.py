import jwt
from django.conf import settings
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED, \
    HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from srt.users.models import User
from srt.users.serializers import StaffUserSerializer, UserSerializer
from srt.users.tests.factories import StaffUserFactory, UserFactory
from srt.core.tests import BaseTestCase


class UserViewSetTestCase(BaseTestCase):
    list_url = 'user-list'
    detail_url = 'user-detail'

    def setUp(self):
        self.staff_user = StaffUserFactory()
        self.simple_user = UserFactory()

    def test_permission_classes__only_is_authenticated_user_allows_access(self):
        response = self.client.get(self.get_list_url())
        assert response.status_code == HTTP_401_UNAUTHORIZED
        self.client.force_authenticate(self.staff_user)
        response = self.client.get(self.get_list_url())
        assert response.status_code == HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_permission_classes__staff_allow_to_use_any_rest_method(self):
        self.client.force_authenticate(self.staff_user)

        # POST
        assert User.objects.count() == 2
        data = {'email': self.fake.email(), 'password': self.fake.password()}
        response = self.client.post(self.get_list_url(), data=data)
        assert response.status_code == HTTP_201_CREATED
        assert User.objects.count() == 3
        user = User.objects.get(email=data['email'])
        self.assert_fields(user, data, self.staff_user)

        # GET(id)
        response = self.client.get(self.get_detail_url(response.data['id']))
        assert response.status_code == HTTP_200_OK
        assert response.data['email'] == data['email']
        serializer = StaffUserSerializer(user)
        assert response.data == serializer.data

        # PATCH
        data = {'full_name': f'{self.fake.first_name()} {self.fake.last_name()}'}
        response = self.client.patch(self.get_detail_url(response.data['id']), data=data)
        user.refresh_from_db()
        assert response.status_code == HTTP_200_OK
        assert response.data['full_name'] == data['full_name']
        assert user.full_name == data['full_name']

        # PUT
        data = {**response.data, **{'full_name': f'{self.fake.first_name()} {self.fake.last_name()}'}}
        response = self.client.put(self.get_detail_url(response.data['id']), data=data)
        user.refresh_from_db()
        assert response.status_code == HTTP_200_OK
        assert response.data['full_name'] == data['full_name']
        assert user.full_name == data['full_name']

        # DELETE
        assert User.objects.count() == 3
        response = self.client.delete(self.get_detail_url(response.data['id']))
        assert response.status_code == HTTP_204_NO_CONTENT
        assert User.objects.count() == 2

        # GET(all)
        [UserFactory(email=email) for email in [self.fake.email, self.fake.email()]]
        users = User.objects.all()
        response = self.client.get(self.get_list_url())
        assert response.status_code == HTTP_200_OK
        assert len(response.data['results']) == 4
        serializer = StaffUserSerializer(users, many=True)
        assert response.data['results'] == serializer.data
        assert set(entity['id'] for entity in response.data['results']) == set(entity.id for entity in users)

    def test_permission_classes__non_staff_allow_to_use_subset_of_rest_api_methods(self):
        self.client.force_authenticate(self.simple_user)

        # POST
        assert User.objects.count() == 2
        data = {'email': self.fake.email(), 'password': self.fake.password()}
        response = self.client.post(self.get_list_url(), data=data)
        assert response.status_code == HTTP_403_FORBIDDEN
        assert User.objects.count() == 2

        # GET(id)
        response = self.client.get(self.get_detail_url(self.simple_user.id))
        assert response.status_code == HTTP_200_OK
        serializer = UserSerializer(self.simple_user)
        assert response.data == serializer.data

        # PATCH
        data = {'full_name': f'{self.fake.first_name()} {self.fake.last_name()}'}
        response = self.client.patch(self.get_detail_url(self.simple_user.id), data=data)
        self.simple_user.refresh_from_db()
        assert response.status_code == HTTP_200_OK
        assert response.data['full_name'] == data['full_name']
        assert self.simple_user.full_name == data['full_name']

        # PUT
        data = {**response.data, **{'full_name': f'{self.fake.first_name()} {self.fake.last_name()}'}}
        response = self.client.put(self.get_detail_url(self.simple_user.id), data=data)
        self.simple_user.refresh_from_db()
        assert response.status_code == HTTP_403_FORBIDDEN
        assert self.simple_user.full_name != data['full_name']

        # DELETE
        response = self.client.delete(self.get_detail_url(self.simple_user.id))
        assert response.status_code == HTTP_403_FORBIDDEN
        assert User.objects.count() == 2

        # GET(all)
        [UserFactory(email=email) for email in [self.fake.email(), self.fake.email()]]
        users = User.objects.filter(email=self.simple_user.email)
        response = self.client.get(self.get_list_url())
        assert response.status_code == HTTP_200_OK
        assert len(response.data['results']) == 1
        serializer = UserSerializer(users, many=True)
        assert response.data['results'] == serializer.data
        assert set(entity['id'] for entity in response.data['results']) == set(entity.id for entity in users)

    def test_permission_classes__staff_allows_to_access_and_modify_any_other_users_data(self):
        self.client.force_authenticate(self.staff_user)

        # POST
        assert User.objects.count() == 2
        data = {'email': self.fake.email(), 'password': self.fake.password()}
        response = self.client.post(self.get_list_url(), data=data)
        assert response.status_code == HTTP_201_CREATED
        assert response.data['email'] == data['email']
        user = User.objects.get(email=data['email'])
        self.assert_fields(user, data, self.simple_user)

        # GET(id)
        response = self.client.get(self.get_detail_url(response.data['id']))
        assert response.status_code == HTTP_200_OK
        serializer = StaffUserSerializer(user)
        assert response.data == serializer.data

        # PATCH
        data = {'full_name': f'{self.fake.first_name()} {self.fake.last_name()}'}
        response = self.client.patch(self.get_detail_url(response.data['id']), data=data)
        user.refresh_from_db()
        assert response.status_code == HTTP_200_OK
        assert response.data['full_name'] == data['full_name']
        assert user.full_name == data['full_name']

        # PUT
        data = {**response.data, **{'full_name': f'{self.fake.first_name()} {self.fake.last_name()}'}}
        response = self.client.put(self.get_detail_url(response.data['id']), data=data)
        user.refresh_from_db()
        assert response.status_code == HTTP_200_OK
        assert response.data['full_name'] == data['full_name']
        assert user.full_name == data['full_name']

        # DELETE
        assert User.objects.count() == 3
        response = self.client.delete(self.get_detail_url(response.data['id']))
        assert response.status_code == HTTP_204_NO_CONTENT
        assert User.objects.count() == 2

        # GET(all)
        [UserFactory(email=email) for email in [self.fake.email(), self.fake.email()]]
        users = User.objects.all()
        response = self.client.get(self.get_list_url())
        assert response.status_code == HTTP_200_OK
        assert len(response.data['results']) == 4
        serializer = StaffUserSerializer(users, many=True)
        assert response.data['results'] == serializer.data
        assert set(entity['id'] for entity in response.data['results']) == set(entity.id for entity in users)

    def test_permission_classes__non_staff_allows_to_access_and_modify_only_his_data(self):
        self.client.force_authenticate(self.simple_user)

        # POST
        assert User.objects.count() == 2
        data = {'email': self.fake.email(), 'password': self.fake.password()}
        response = self.client.post(self.get_list_url(), data=data)
        assert response.status_code == HTTP_403_FORBIDDEN
        assert User.objects.count() == 2

        # GET(id)
        response = self.client.get(self.get_detail_url(self.staff_user.id))
        assert response.status_code == HTTP_404_NOT_FOUND

        # PATCH
        data = {'full_name': f'{self.fake.first_name()} {self.fake.last_name()}'}
        response = self.client.patch(self.get_detail_url(self.staff_user.id), data=data)
        assert response.status_code == HTTP_404_NOT_FOUND

        # DELETE
        response = self.client.delete(self.get_detail_url(self.staff_user.id))
        assert response.status_code == HTTP_403_FORBIDDEN

        # GET(all)
        [UserFactory(email=email) for email in [self.fake.email(), self.fake.email()]]
        users = User.objects.filter(email=self.simple_user.email)
        response = self.client.get(self.get_list_url())
        assert response.status_code == HTTP_200_OK
        assert len(response.data['results']) == 1
        assert User.objects.count() == 4
        serializer = UserSerializer(users, many=True)
        assert response.data['results'] == serializer.data

    def test_get_serializer_class__staff_user_serializer(self):
        self.client.force_authenticate(self.staff_user)
        response = self.client.get(self.get_detail_url(self.staff_user.id))
        serializer = StaffUserSerializer(self.staff_user)
        assert response.status_code == HTTP_200_OK
        assert response.data == serializer.data

    def test_get_serializer_class__user_serializer(self):
        self.client.force_authenticate(self.simple_user)
        response = self.client.get(self.get_detail_url(self.simple_user.id))
        serializer = UserSerializer(self.simple_user)
        assert response.status_code == HTTP_200_OK
        assert response.data == serializer.data

    def test_get_serializer_class__staff_user_allow_to_modify_all_fields(self):
        user = UserFactory()
        self.client.force_authenticate(self.staff_user)
        data = {'email': 'staff.new@gmail.com', 'is_staff': True}
        response = self.client.patch(self.get_detail_url(user.id), data=data)
        user.refresh_from_db()
        for field in data.keys():
            assert response.data[field] == data[field]
            assert getattr(user, field) == data[field]

    def test_get_serializer_class__non_staff_user_allow_to_modify_non_read_only_fields(self):
        self.client.force_authenticate(self.simple_user)
        data = {'email': 'staff.new@gmail.com', 'is_staff': True}
        response = self.client.patch(self.get_detail_url(self.simple_user.id), data=data)
        assert response.status_code == HTTP_200_OK
        self.simple_user.refresh_from_db()
        for field in data.keys():
            assert getattr(self.simple_user, field) != data[field]
        data = {'full_name': self.fake.name()}
        response = self.client.patch(self.get_detail_url(self.simple_user.id), data=data)
        assert response.status_code == HTTP_200_OK
        self.simple_user.refresh_from_db()
        for field in data.keys():
            assert getattr(self.simple_user, field) == data[field]


class srtTokenObtainTestCase(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        data = {'email': settings.TEST_STAFFUSER_EMAIL, 'password': settings.TEST_STAFFUSER_PASSWORD}
        cls.staff_user = User.objects.create_superuser(**data)
        data = {'email': settings.TEST_SIMPLEUSER_EMAIL, 'password': settings.TEST_SIMPLEUSER_PASSWORD}
        cls.simple_user = User.objects.create_user(**data)

    def test_token_obtain__staff_user_correct_credentials(self):
        data = {'email': settings.TEST_STAFFUSER_EMAIL, 'password': settings.TEST_STAFFUSER_PASSWORD}
        token = self.client.post(reverse('auth'), data).data['token']
        assert len(token) > 100
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        assert decoded['token_type'] == 'access'
        assert decoded['user_id'] == self.staff_user.id
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        response = self.client.get(reverse('user-detail', args=[self.staff_user.id]))
        assert response.status_code == HTTP_200_OK
        assert all([key in response.data for key in StaffUserSerializer.Meta.fields])

    def test_token_obtain__staff_user_incorrect_credentials_user_exist(self):
        data = {'email': settings.TEST_SIMPLEUSER_EMAIL, 'password': 'password'}
        response = self.client.post(reverse('auth'), data)
        assert response.status_code == HTTP_401_UNAUTHORIZED

    def test_token_obtain__staff_user_incorrect_credentials_user_not_exist(self):
        data = {'email': 'test@gmail.com', 'password': 'password'}
        response = self.client.post(reverse('auth'), data)
        assert response.status_code == HTTP_401_UNAUTHORIZED

    def test_token_obtain__simpleuser_correct_credentials(self):
        data = {'email': settings.TEST_SIMPLEUSER_EMAIL, 'password': settings.TEST_SIMPLEUSER_PASSWORD}
        token = self.client.post(reverse('auth'), data).data['token']
        assert len(token) > 100
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        assert decoded['token_type'] == 'access'
        assert decoded['user_id'] == self.simple_user.id
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        response = self.client.get(reverse('user-detail', args=[self.simple_user.id]))
        assert response.status_code == HTTP_200_OK
        assert all([key in response.data for key in UserSerializer.Meta.fields])


class ChangePasswordTestCase(BaseTestCase):

    def test_permission_classes__only_is_authenticated_user_allows_access(self):
        pass  # TODO:
