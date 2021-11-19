from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from poco_common.core.models import GrabberSettings, GrabberSettingsRecords, make_slug
from poco_common.exchange.serializers import GrabberSettingsSerializer


GRABBER_SETTINGS_URL = reverse('data_grabber:grabbersettings-list')


class PublicGrabberSettingsApiTests(TestCase):
    """Test the publicly available grabber settings API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving grabber settings"""
        res = self.client.get(GRABBER_SETTINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateGrabberSettingsApiTests(TestCase):
    """Test the authorized user grabber settings API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@poco.com',
            'password123',
            name='test'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_grabber_settings(self):
        """Test retrieving retrieve_grabber"""
        account_key = make_slug()
        grabber_settings = GrabberSettings.objects.create(
            user=self.user,
            symbols=['BTCBNB', 'BTCADA'],
            account_keys=[account_key],
            state=GrabberSettings.STATE_INACTIVE
        )
        res = self.client.get(GRABBER_SETTINGS_URL)
        grabber_settings_res = GrabberSettings.objects.all()
        serializer = GrabberSettingsSerializer(grabber_settings_res, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(grabber_settings.slug, serializer.data[0]['slug'])
        self.assertEqual(len(serializer.data), 1)

    def test_retrieve_grabber_settings_works_as_singleton(self):
        """Test retrieving tags"""
        account_key = make_slug()
        grabber_settings = GrabberSettings.objects.create(
            user=self.user,
            symbols=['BTCBNB', 'BTCADA'],
            account_keys=[account_key],
            state=GrabberSettings.STATE_INACTIVE
        )

        res = self.client.get(GRABBER_SETTINGS_URL)

        grabber_settings_res = GrabberSettings.objects.all()
        serializer = GrabberSettingsSerializer(grabber_settings_res, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(grabber_settings.slug, serializer.data[0]['slug'])
        self.assertEqual(len(serializer.data), 1)

        res = self.client.get(GRABBER_SETTINGS_URL)

        grabber_settings_res = GrabberSettings.objects.all()
        serializer = GrabberSettingsSerializer(grabber_settings_res, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(grabber_settings.slug, serializer.data[0]['slug'])
        self.assertEqual(len(serializer.data), 1)

    def test_create_grabber_settings(self):
        """Test creating a new grabber settings with valid payload"""

        payload = {
            'user': self.user.id,
            'is_running': True,
            'symbols': ['btcada', 'btcbnb'],
            'account_keys': ['aaaaaaa'],
            'state': GrabberSettings.STATE_ACTIVE
        }
        res = self.client.post(GRABBER_SETTINGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        grabber_settings_res = GrabberSettings.objects.all()
        grabber_setting = grabber_settings_res[0]
        self.assertEqual(grabber_setting.user.id, self.user.id)
        self.assertTrue(grabber_setting.is_running)
        self.assertEqual(grabber_setting.state, GrabberSettings.STATE_ACTIVE)
        self.assertEqual(grabber_setting.account_keys, ['aaaaaaa'])
        self.assertEqual(grabber_setting.symbols, ['btcada', 'btcbnb'])

        grabber_settings_records = GrabberSettingsRecords.objects.all()
        self.assertEqual(grabber_settings_records.count(), 1)
        grabber_settings_record = grabber_settings_records[0]

        self.assertEqual(grabber_settings_record.slug, grabber_setting.slug)
        self.assertEqual(grabber_settings_record.is_running, grabber_setting.is_running)
        self.assertEqual(grabber_settings_record.symbols, grabber_setting.symbols)
        self.assertEqual(grabber_settings_record.account_keys, grabber_setting.account_keys)
        self.assertEqual(grabber_settings_record.state, grabber_setting.state)
        self.assertEqual(grabber_settings_record.user, grabber_setting.user)
        self.assertEqual(grabber_settings_record.created, grabber_setting.created)
        self.assertEqual(grabber_settings_record.updated, grabber_setting.updated)
        self.assertTrue(grabber_settings_record.is_record_created)
        self.assertIsNotNone(grabber_settings_record.slug_record)
        self.assertNotEqual(grabber_settings_record.slug_record, grabber_settings_record.slug)
        self.assertIsNotNone(grabber_settings_record.created_record)

    def test_create_grabber_settings_invalid(self):
        """Test creating a new grabber settings with invalid payload"""
        payload = {
            'user': 0,
            'is_running': True,
        }
        res = self.client.post(GRABBER_SETTINGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_grabber_settings(self):
        """Test updating grabber settings with valid payload"""
        account_key = make_slug()
        grabber_settings = GrabberSettings.objects.create(
            user=self.user,
            symbols=['BTCBNB', 'BTCADA'],
            account_keys=[account_key],
            state=GrabberSettings.STATE_INACTIVE,
            is_running=False
        )
        updated = grabber_settings.updated
        payload = {
            'is_running': True,
        }
        self.assertEqual(payload['is_running'], True)
        res = self.client.patch(reverse('data_grabber:grabbersettings-detail',
                                        kwargs={'slug': grabber_settings.slug}), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        grabber_settings_res = GrabberSettings.objects.all()
        grabber_setting = grabber_settings_res[0]
        new_updated = grabber_setting.updated
        self.assertEqual(grabber_setting.is_running, True)
        self.assertGreater(new_updated, updated)

        grabber_settings_records = GrabberSettingsRecords.objects.all()
        self.assertEqual(grabber_settings_records.count(), 2)
        grabber_settings_record = grabber_settings_records.filter(
            updated=grabber_setting.updated)[0]

        self.assertEqual(grabber_settings_record.slug, grabber_setting.slug)
        self.assertEqual(grabber_settings_record.is_running, grabber_setting.is_running)
        self.assertEqual(grabber_settings_record.symbols, grabber_setting.symbols)
        self.assertEqual(grabber_settings_record.account_keys, grabber_setting.account_keys)
        self.assertEqual(grabber_settings_record.state, grabber_setting.state)
        self.assertEqual(grabber_settings_record.user, grabber_setting.user)
        self.assertEqual(grabber_settings_record.created, grabber_setting.created)
        self.assertEqual(grabber_settings_record.updated, grabber_setting.updated)
        self.assertFalse(grabber_settings_record.is_record_created)
        self.assertIsNotNone(grabber_settings_record.slug_record)
        self.assertNotEqual(grabber_settings_record.slug_record, grabber_settings_record.slug)
        self.assertIsNotNone(grabber_settings_record.created_record)
