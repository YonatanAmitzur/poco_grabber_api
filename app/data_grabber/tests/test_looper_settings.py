from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import LooperSettings, GrabberRun, make_slug
from exchange.serializers import LooperSettingsSerializer


LOOPER_SETTINGS_URL = reverse('data_grabber:loopersettings-list')


class PublicLooperSettingsApiTests(TestCase):
    """Test the publicly available LooperSettings API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving LooperSettings"""
        res = self.client.get(LOOPER_SETTINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateLooperSettingsApiTests(TestCase):
    """Test the authorized user LooperSettings API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@poco.com',
            'password123',
            name='test'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_looper_settings(self):
        """Test retrieving retrieve_looper"""
        grabber_run_slug = make_slug()
        grabber_run = GrabberRun.objects.create(
            slug=grabber_run_slug,
            user=self.user
        )
        looper_settings = LooperSettings.objects.create(
            grabber_run_slug=grabber_run.slug,
            user=self.user
        )

        res = self.client.get(LOOPER_SETTINGS_URL)

        looper_settings_res = LooperSettings.objects.all()
        serializer = LooperSettingsSerializer(looper_settings_res, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(looper_settings.slug, serializer.data[0]['slug'])
        self.assertEqual(len(serializer.data), 1)

    def test_retrieve_looper_settings_by_run_type(self):
        """Test retrieving retrieve_looper by run_type"""
        grabber_run_slug = make_slug()
        grabber_run = GrabberRun.objects.create(
            slug=grabber_run_slug,
            user=self.user
        )
        looper_settings = LooperSettings.objects.create(
            grabber_run_slug=grabber_run.slug,
            user=self.user,
            run_type=LooperSettings.RUN_TYPE_UPDATE_PAIRS_ONLY
        )

        res = self.client.get(LOOPER_SETTINGS_URL,
                              {'run_type': LooperSettings.RUN_TYPE_UPDATE_BALANCES_ONLY})
        self.assertEqual(res.data, [])

        res = self.client.get(LOOPER_SETTINGS_URL, {
            'run_type': LooperSettings.RUN_TYPE_UPDATE_PAIRS_ONLY})

        looper_settings_res = LooperSettings.objects.all()
        serializer = LooperSettingsSerializer(looper_settings_res, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(looper_settings.slug, serializer.data[0]['slug'])
        self.assertEqual(len(serializer.data), 1)

    def test_retrieve_looper_settings_by_is_running(self):
        """Test retrieving retrieve_looper by is_running"""
        grabber_run_slug = make_slug()
        grabber_run = GrabberRun.objects.create(
            slug=grabber_run_slug,
            user=self.user
        )
        looper_settings = LooperSettings.objects.create(
            grabber_run_slug=grabber_run.slug,
            user=self.user,
            is_running=True
        )

        res = self.client.get(LOOPER_SETTINGS_URL, {'is_running': 0})
        self.assertEqual(res.data, [])

        res = self.client.get(LOOPER_SETTINGS_URL, {'is_running': 1})

        looper_settings_res = LooperSettings.objects.all()
        serializer = LooperSettingsSerializer(looper_settings_res, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(looper_settings.slug, serializer.data[0]['slug'])
        self.assertEqual(len(serializer.data), 1)

    def test_retrieve_looper_settings_by_run_type_and_is_running(self):
        """Test retrieving retrieve_looper by run_type and is_running"""
        grabber_run_slug = make_slug()
        grabber_run = GrabberRun.objects.create(
            slug=grabber_run_slug,
            user=self.user
        )
        looper_settings = LooperSettings.objects.create(
            grabber_run_slug=grabber_run.slug,
            user=self.user,
            is_running=True,
            run_type=LooperSettings.RUN_TYPE_UPDATE_PAIRS_ONLY
        )

        res = self.client.get(LOOPER_SETTINGS_URL, {'is_running': 0})
        self.assertEqual(res.data, [])

        res = self.client.get(LOOPER_SETTINGS_URL,
                              {'run_type': LooperSettings.RUN_TYPE_UPDATE_BALANCES_ONLY})
        self.assertEqual(res.data, [])

        res = self.client.get(LOOPER_SETTINGS_URL,
                              {'is_running': 0,
                               'run_type': LooperSettings.RUN_TYPE_UPDATE_BALANCES_ONLY})
        self.assertEqual(res.data, [])

        res = self.client.get(LOOPER_SETTINGS_URL,
                              {'is_running': 1,
                               'run_type': LooperSettings.RUN_TYPE_UPDATE_PAIRS_ONLY})

        looper_settings_res = LooperSettings.objects.all()
        serializer = LooperSettingsSerializer(looper_settings_res, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(looper_settings.slug, serializer.data[0]['slug'])
        self.assertEqual(len(serializer.data), 1)

    def test_retrieve_looper_settings_works_as_singleton(self):
        """Test retrieving tags"""
        grabber_run_slug = make_slug()
        grabber_run = GrabberRun.objects.create(
            slug=grabber_run_slug,
            user=self.user
        )
        looper_settings = LooperSettings.objects.create(
            grabber_run_slug=grabber_run.slug,
            user=self.user,
            run_type=LooperSettings.RUN_TYPE_UPDATE_PAIRS_ONLY
        )

        res = self.client.get(LOOPER_SETTINGS_URL)

        looper_settings_res = LooperSettings.objects.all()
        serializer = LooperSettingsSerializer(looper_settings_res, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(looper_settings.slug, serializer.data[0]['slug'])
        self.assertEqual(len(serializer.data), 1)
        self.assertEqual(serializer.data[0]['run_type'], LooperSettings.RUN_TYPE_UPDATE_PAIRS_ONLY)

        res = self.client.get(LOOPER_SETTINGS_URL)

        looper_settings_res = LooperSettings.objects.all()
        serializer = LooperSettingsSerializer(looper_settings_res, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(looper_settings.slug, serializer.data[0]['slug'])
        self.assertEqual(len(serializer.data), 1)
        self.assertEqual(serializer.data[0]['run_type'], LooperSettings.RUN_TYPE_UPDATE_PAIRS_ONLY)

        grabber_run_2 = GrabberRun.objects.create(
            slug=grabber_run_slug,
            user=self.user
        )
        LooperSettings.objects.update(
            grabber_run_slug=grabber_run_2.slug,
            user=self.user,
            run_type=LooperSettings.RUN_TYPE_UPDATE_BALANCES_ONLY
        )

        res_2 = self.client.get(LOOPER_SETTINGS_URL)

        looper_settings_res_2 = LooperSettings.objects.all()
        serializer_2 = LooperSettingsSerializer(looper_settings_res_2, many=True)
        self.assertEqual(res_2.status_code, status.HTTP_200_OK)
        self.assertEqual(res_2.data, serializer_2.data)
        self.assertNotEqual(grabber_run_2.slug, serializer_2.data[0]['slug'])
        self.assertEqual(len(serializer_2.data), 1)
        self.assertEqual(serializer.data[0]['run_type'], LooperSettings.RUN_TYPE_UPDATE_PAIRS_ONLY)

    def test_looper_settings_limited_to_user(self):
        """Test that looper_settings returned are for the authenticated user"""
        grabber_run_slug = make_slug()
        grabber_run = GrabberRun.objects.create(
            slug=grabber_run_slug,
            user=self.user
        )
        LooperSettings.objects.create(
            grabber_run_slug=grabber_run.slug,
            user=self.user,
            run_type=LooperSettings.RUN_TYPE_UPDATE_BALANCES_ONLY
        )

        user2 = get_user_model().objects.create_user(
            'other@poco.com',
            'testpass',
            name='test'
        )
        grabber_run_slug_2 = make_slug()
        GrabberRun.objects.create(
            slug=grabber_run_slug_2,
            user=user2,
        )
        LooperSettings.objects.update(
            grabber_run_slug=grabber_run.slug,
            user=user2,
            run_type=LooperSettings.RUN_TYPE_UPDATE_PAIRS_ONLY
        )

        res = self.client.get(LOOPER_SETTINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [])

    def test_create_looper_settings_successful(self):
        """Test creating a new looper settings"""
        slug = make_slug()
        grabber_run = GrabberRun.objects.create(
            slug=slug,
            user=self.user
        )
        payload = {'grabber_run_slug': grabber_run,
                   'run_type': LooperSettings.RUN_TYPE_UPDATE_BALANCES_ONLY,
                   'user': self.user.id}

        res = self.client.post(LOOPER_SETTINGS_URL, payload)

        looper_settings = LooperSettings.objects.all()
        serializer = LooperSettingsSerializer(looper_settings, many=True)
        self.assertTrue(looper_settings)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, serializer.data[0])
        self.assertEqual(looper_settings[0].slug, serializer.data[0]['slug'])
        self.assertEqual(len(serializer.data), 1)

    def test_create_looper_settings_invalid(self):
        """Test creating a new looper settings with invalid payload"""
        payload = {
            'grabber_run_slug': '',
        }
        res = self.client.post(LOOPER_SETTINGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
