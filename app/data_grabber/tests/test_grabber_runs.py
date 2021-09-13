from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import GrabberRun, make_slug
from exchange.serializers import GrabberRunSerializer


GRABBER_RUN_URL = reverse('data_grabber:grabberrun-list')


class PublicGrabberRunApiTests(TestCase):
    """Test the publicly available grabber runs API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving grabber runs"""
        res = self.client.get(GRABBER_RUN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateGrabberRunApiTests(TestCase):
    """Test the authorized user grabber runs API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@poco.com',
            'password123',
            name='test'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_grabber_run(self):
        """Test retrieving grabber run"""
        grabber_run_slug = make_slug()
        grabber_run = GrabberRun.objects.create(
            slug=grabber_run_slug,
            user=self.user
        )

        res = self.client.get(GRABBER_RUN_URL)

        grabber_run_res = GrabberRun.objects.all()
        serializer = GrabberRunSerializer(grabber_run_res, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(grabber_run.slug, serializer.data[0]['slug'])
        self.assertEqual(len(serializer.data), 1)

    def test_retrieve_grabber_run_by_status(self):
        """Test retrieving grabber_run by run_type"""
        grabber_run_slug = make_slug()
        grabber_run = GrabberRun.objects.create(
            slug=grabber_run_slug,
            user=self.user,
            status=GrabberRun.STATUS_ACTIVE
        )

        res = self.client.get(GRABBER_RUN_URL, {'status': GrabberRun.STATUS_CREATED})
        self.assertEqual(res.data, [])

        res = self.client.get(GRABBER_RUN_URL, {
            'status': GrabberRun.STATUS_ACTIVE})

        grabber_run_res = GrabberRun.objects.all()
        serializer = GrabberRunSerializer(grabber_run_res, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(grabber_run.slug, serializer.data[0]['slug'])
        self.assertEqual(len(serializer.data), 1)

    def test_grabber_run_limited_to_user(self):
        """Test that grabber_run returned are for the authenticated user"""
        grabber_run_slug = make_slug()
        GrabberRun.objects.create(
            slug=grabber_run_slug,
            user=self.user
        )

        user2 = get_user_model().objects.create_user(
            'other@poco.com',
            'testpass',
            name='test'
        )
        grabber_run_slug_2 = make_slug()
        GrabberRun.objects.update(
            slug=grabber_run_slug_2,
            user=user2,
        )

        res = self.client.get(GRABBER_RUN_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [])

    def test_create_grabber_run_successful(self):
        """Test creating a new looper settings"""
        payload = {'status': GrabberRun.STATUS_ACTIVE,
                   'user': self.user.id}

        res = self.client.post(GRABBER_RUN_URL, payload)

        grabber_run = GrabberRun.objects.all()
        serializer = GrabberRunSerializer(grabber_run, many=True)
        self.assertTrue(grabber_run)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, serializer.data[0])
        self.assertEqual(grabber_run[0].slug, serializer.data[0]['slug'])
        self.assertEqual(len(serializer.data), 1)

    def test_create_grabber_run_invalid(self):
        """Test creating a new grabber run with invalid payload"""
        payload = {
            'status': '',
        }
        res = self.client.post(GRABBER_RUN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
