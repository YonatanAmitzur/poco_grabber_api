# import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from core.models import User, GrabberRun, LooperSettings, SymbolInfo, make_slug


def sample_user(email='test@poco.com', password='testpass'):
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
        user = get_user_model().objects.create_user(email, 'test123', name=name)

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
            'test123'
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
        # now_minus_one_minute = datetime.datetime.now() - datetime.timedelta(seconds=30)
        # difference_created = datetime.datetime.utcnow() - user.created.replace(tzinfo=None)
        # difference_updated = datetime.datetime.utcnow() - user.updated.replace(tzinfo=None)
        # self.assertLessEqual(difference_created.microseconds, now_minus_one_minute.microsecond)
        # self.assertGreaterEqual(now_minus_one_minute.microsecond, difference_created.microseconds)
        # self.assertLessEqual(difference_updated.microseconds, now_minus_one_minute.microsecond)
        # self.assertGreaterEqual(now_minus_one_minute.microsecond, difference_updated.microseconds)
        self.assertIsNotNone(user.slug)
        self.assertEqual(len(user.slug), 32)
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_superuser, False)
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_test, False)
        self.assertEqual(user.client_tier, User.STANDARD)
        self.assertEqual(user.status, User.STATUS_CREATED)

    def test_create_symbol_info(self):
        symbol_info = SymbolInfo.objects.create(
            symbol='ETHBTC',
            status='TRADING',
            baseAsset='ETH',
            baseAssetPrecision=8,
            quoteAsset='BTC',
            quotePrecision=8,
            quoteAssetPrecision=8,
            baseCommissionPrecision=8,
            quoteCommissionPrecision=8,
            orderTypes=['LIMIT', 'LIMIT_MAKER', 'MARKET', 'STOP_LOSS_LIMIT', 'TAKE_PROFIT_LIMIT'],
            icebergAllowed=True,
            ocoAllowed=True,
            quoteOrderQtyMarketAllowed=True,
            isSpotTradingAllowed=True,
            isMarginTradingAllowed=True,
            filters=[
                {'filterType': 'PRICE_FILTER',
                 'minPrice': '0.00000100',
                 'maxPrice': '922327.00000000',
                 'tickSize': '0.00000100'},
                {'filterType': 'PERCENT_PRICE',
                 'multiplierUp': '5',
                 'multiplierDown': '0.2',
                 'avgPriceMins': 5},
                {'filterType': 'LOT_SIZE',
                 'minQty': '0.00100000',
                 'maxQty': '100000.00000000',
                 'stepSize': '0.00100000'},
                {'filterType': 'MIN_NOTIONAL',
                 'minNotional': '0.00010000',
                 'applyToMarket': True,
                 'avgPriceMins': 5},
                {'filterType': 'ICEBERG_PARTS',
                 'limit': 10},
                {'filterType': 'MARKET_LOT_SIZE',
                 'minQty': '0.00000000',
                 'maxQty': '1127.04279986',
                 'stepSize': '0.00000000'},
                {'filterType': 'MAX_NUM_ORDERS',
                 'maxNumOrders': 200},
                {'filterType': 'MAX_NUM_ALGO_ORDERS',
                 'maxNumAlgoOrders': 5}],
            permissions=['SPOT', 'MARGIN']
        )

        self.assertEqual(str(symbol_info), symbol_info.symbol)

    def test_create_looper_settings(self):
        grabber_run_slug = make_slug()
        curr_user = get_user_model().objects.create_user(
            email='test@poco.com',
            password='testpass',
            name='test'
        )
        grabber_run = GrabberRun.objects.create(
            slug=grabber_run_slug,
            user=curr_user
        )
        looper_settings = LooperSettings.objects.create(
            grabber_run_slug=grabber_run.slug,
            user=curr_user
        )
        self.assertEqual(looper_settings.grabber_run_slug, grabber_run.slug)
        self.assertIsNotNone(looper_settings.slug)
        self.assertIsNone(looper_settings.run_type)
        self.assertIsNone(looper_settings.is_running)
        self.assertIsNotNone(looper_settings.created)
        self.assertIsNotNone(looper_settings.updated)
        self.assertEqual(looper_settings.user, curr_user)

    def test_create_grabber_run(self):
        slug = make_slug()
        curr_user = get_user_model().objects.create_user(
            email='test@poco.com',
            password='testpass',
            name='test'
        )
        grabber_run = GrabberRun.objects.create(
            slug=slug,
            user=curr_user
        )

        self.assertEqual(grabber_run.slug, slug)
        self.assertIsNotNone(grabber_run.created)
        self.assertIsNotNone(grabber_run.updated)
        self.assertEqual(grabber_run.user, curr_user)
        self.assertEqual(grabber_run.status, GrabberRun.STATUS_CREATED)
