import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from core.models import User


def sample_user(email='test@londonappdev.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@poco.com'
        password = 'Testpass123'
        name = 'test'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            name=name
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@POCO.COM'
        name = 'test'
        user = get_user_model().objects.create_user(email, 'test123', name='test')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValidationError) as exception_cm:
            get_user_model().objects.create_user(None, 'test123', name='test')

        exception = exception_cm.exception
        self.assertIn('This field cannot be blank.', exception.messages)
        self.assertEqual(exception.message_dict['email'], ['This field cannot be blank.'])

    def test_new_user_invalid_name(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValidationError) as exception_cm:
            get_user_model().objects.create_user('test@poco.com', 'test123')

        exception = exception_cm.exception
        self.assertIn('This field cannot be blank.', exception.messages)
        self.assertEqual(exception.message_dict['name'], ['This field cannot be blank.'])

    def test_new_user_invalid_email_and_name(self):
        with self.assertRaises(ValidationError) as exception_cm:
            get_user_model().objects.create_user(None, 'test123')

        exception = exception_cm.exception
        self.assertIn('This field cannot be blank.', exception.messages)
        self.assertEqual(exception.message_dict['name'], ['This field cannot be blank.'])
        self.assertEqual(exception.message_dict['email'], ['This field cannot be blank.'])

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@poco.com',
            'test123',
            name='test'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_user_default_values(self):
        """Test creating a new user with an email is successful"""
        email = 'test@poco.com'
        password = 'Testpass123'
        name = 'test'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            name=name
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.name, 'test')
        self.assertTrue(user.check_password(password))
        # default values
        now_minus_one_minute = datetime.datetime.now() - datetime.timedelta(minutes=1)
        difference_created = datetime.datetime.utcnow() - user.created.replace(tzinfo=None)
        difference_updated = datetime.datetime.utcnow() - user.updated.replace(tzinfo=None)
        self.assertLessEqual(difference_created.microseconds, now_minus_one_minute.microsecond)
        self.assertGreaterEqual(now_minus_one_minute.microsecond, difference_created.microseconds)
        self.assertLessEqual(difference_updated.microseconds, now_minus_one_minute.microsecond)
        self.assertGreaterEqual(now_minus_one_minute.microsecond, difference_updated.microseconds)
        self.assertIsNotNone(user.slug)
        self.assertEqual(len(user.slug), 32)
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_superuser, False)
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_test, False)
        self.assertEqual(user.client_tier, User.STANDARD)
        self.assertEqual(user.status, User.STATUS_CREATED)



