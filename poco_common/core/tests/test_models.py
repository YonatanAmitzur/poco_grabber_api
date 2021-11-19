# import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from poco_common.core.models import User, GrabberRun, GrabberSettings, SymbolInfo, \
    BinanceAccount, make_slug


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

    def test_create_grabber_settings(self):
        account_key = make_slug()
        curr_user = get_user_model().objects.create_user(
            email='test@poco.com',
            password='testpass',
            name='test'
        )
        grabber_settings = GrabberSettings.objects.create(
            user=curr_user,
            symbols=['BTCBNB', 'BTCADA'],
            account_keys=[account_key],
            state=GrabberSettings.STATE_INACTIVE

        )
        self.assertIsNotNone(grabber_settings.slug)
        self.assertEqual(grabber_settings.state, GrabberSettings.STATE_INACTIVE)
        self.assertFalse(grabber_settings.is_running)
        self.assertListEqual(grabber_settings.symbols, ['BTCBNB', 'BTCADA'])
        self.assertListEqual(grabber_settings.account_keys, [account_key])
        self.assertIsNotNone(grabber_settings.created)
        self.assertIsNotNone(grabber_settings.updated)
        self.assertEqual(grabber_settings.user, curr_user)

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

    def test_create_binance_account(self):
        slug = make_slug()
        curr_user = get_user_model().objects.create_user(
            email='test@poco.com',
            password='testpass',
            name='test'
        )

        binance_account = BinanceAccount.objects.create(
            slug=slug,
            user=curr_user,
            makerCommission=10,
            takerCommission=10,
            buyerCommission=0,
            sellerCommission=0,
            canTrade=True,
            canWithdraw=True,
            canDeposit=True,
            updateTime=1612653209207,
            accountType='MARGIN',
            balances=[
                {'asset': 'BTC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'LTC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ETH', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'NEO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BNB', 'free': '0.06198843', 'locked': '0.00000000'},
                {'asset': 'QTUM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'EOS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SNT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BNT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'GAS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BCC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'USDT', 'free': '2842.19890279', 'locked': '0.00000000'},
                {'asset': 'HSR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'OAX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DNT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'MCO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ICN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ZRX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'OMG', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'WTC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'YOYO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'LRC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TRX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SNGLS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'STRAT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BQX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'FUN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'KNC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CDT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'XVG', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'IOTA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SNM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'LINK', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CVC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TNT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'REP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'MDA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'MTL', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SALT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'NULS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SUB', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'STX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'MTH', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ADX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ETC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ENG', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ZEC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AST', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'GNT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DGD', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BAT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DASH', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'POWR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BTG', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'REQ', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'XMR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'EVX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'VIB', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ENJ', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'VEN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ARK', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'XRP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'MOD', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'STORJ', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'KMD', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'RCN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'EDO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DATA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DLT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'MANA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'PPT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'RDN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'GXS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AMB', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ARN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BCPT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CND', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'GVT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'POE', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BTS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'FUEL', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'XZC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'QSP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'LSK', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BCD', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TNB', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ADA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'LEND', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'XLM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CMT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'WAVES', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'WABI', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'GTO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ICX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'OST', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ELF', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AION', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'WINGS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BRD', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'NEBL', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'NAV', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'VIBE', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'LUN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TRIG', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'APPC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CHAT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'RLC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'INS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'PIVX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'IOST', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'STEEM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'NANO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AE', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'VIA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BLZ', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SYS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'RPX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'NCASH', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'POA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ONT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ZIL', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'STORM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'XEM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'WAN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'WPR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'QLC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'GRS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CLOAK', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'LOOM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BCN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TUSD', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ZEN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SKY', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'THETA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'IOTX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'QKC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AGI', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'NXS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'NPXS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'KEY', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'NAS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'MFT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DENT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'IQ', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ARDR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'HOT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'VET', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DOCK', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'POLY', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'VTHO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ONG', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'PHX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'HC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'GO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'PAX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'RVN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DCR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'USDC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'MITH', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BCHABC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BCHSV', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'REN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BTT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'USDS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'FET', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TFUEL', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CELR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'MATIC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ATOM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'PHB', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ONE', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'FTM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BTCB', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'USDSB', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CHZ', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'COS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ALGO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ERD', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DOGE', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BGBP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DUSK', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ANKR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'WIN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TUSDB', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'COCOS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'PERL', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TOMO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BUSD', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BAND', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BEAM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'HBAR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'XTZ', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'NGN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DGB', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'NKN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'GBP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'EUR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'KAVA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'RUB', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'UAH', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ARPA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TRY', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CTXC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AERGO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BCH', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TROY', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BRL', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'VITE', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'FTT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AUD', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'OGN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DREP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BULL', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BEAR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ETHBULL', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ETHBEAR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'XRPBULL', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'XRPBEAR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'EOSBULL', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'EOSBEAR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TCT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'WRX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'LTO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ZAR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'MBL', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'COTI', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BKRW', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BNBBULL', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BNBBEAR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'HIVE', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'STPT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SOL', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'IDRT', 'free': '0.00', 'locked': '0.00'},
                {'asset': 'CTSI', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CHR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BTCUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BTCDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'HNT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'JST', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'FIO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BIDR', 'free': '0.00', 'locked': '0.00'},
                {'asset': 'STMX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'MDT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'PNT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'COMP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'IRIS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'MKR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SXP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SNX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DAI', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ETHUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ETHDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ADAUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ADADOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'LINKUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'LINKDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DOT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'RUNE', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BNBUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BNBDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'XTZUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'XTZDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AVA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BAL', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'YFI', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SRM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ANT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CRV', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SAND', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'OCEAN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'NMR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'LUNA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'IDEX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'RSR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'PAXG', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'WNXM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TRB', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'EGLD', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BZRX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'WBTC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'KSM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SUSHI', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'YFII', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DIA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BEL', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'UMA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'EOSUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TRXUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'EOSDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TRXDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'XRPUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'XRPDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DOTUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DOTDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'NBS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'WING', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SWRV', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'LTCUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'LTCDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CREAM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'UNI', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'OXT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SUN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AVAX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BURGER', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BAKE', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'FLM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SCRT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'XVS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CAKE', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SPARTA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'UNIUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'UNIDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ALPHA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ORN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'UTK', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'NEAR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'VIDT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AAVE', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'FIL', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SXPUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SXPDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'INJ', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'FILDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'FILUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'YFIUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'YFIDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CTK', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'EASY', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AUDIO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BCHUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BCHDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BOT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AXS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AKRO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'HARD', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'KP3R', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'RENBTC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SLP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'STRAX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'UNFI', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CVP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BCHA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'FOR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'FRONT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ROSE', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'MDX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'HEGIC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AAVEUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AAVEDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'PROM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BETH', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SKL', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'GLM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SUSD', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'COVER', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'GHST', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SUSHIUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SUSHIDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'XLMUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'XLMDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DF', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'JUV', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'PSG', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BVND', 'free': '0.00', 'locked': '0.00'},
                {'asset': 'GRT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CELO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TWT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'REEF', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'OG', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ATM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ASR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': '1INCH', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'RIF', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BTCST', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TRU', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DEXE', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CKB', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'FIRO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'LIT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'PROS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'VAI', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SFP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'FXS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DODO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AUCTION', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'UFT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ACM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'PHA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TVK', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BADGER', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'FIS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'OM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'POND', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ALICE', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DEGO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BIFI', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'LINA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'PERP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'RAMP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SUPER', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CFX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TKO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AUTO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'EPS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'PUNDIX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TLM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': '1INCHUP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': '1INCHDOWN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'MIR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BAR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'FORTH', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'EZ', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AR', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ICP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'SHIB', 'free': '0.00', 'locked': '0.00'},
                {'asset': 'GYEN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'POLS', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'MASK', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'LPT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'AGIX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ATA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'NU', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'GTC', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'KLAY', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TORN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'KEEP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'ERN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'BOND', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'MLN', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'C98', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'FLOW', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'QUICK', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'RAY', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'MINA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'QNT', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'CLV', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'XEC', 'free': '0.00', 'locked': '0.00'},
                {'asset': 'ALPACA', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'FARM', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'VGX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'MBOX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'WAXP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'TRIBE', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'GNO', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'USDP', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'DYDX', 'free': '0.00000000', 'locked': '0.00000000'},
                {'asset': 'GALA', 'free': '0.00000000', 'locked': '0.00000000'}],
            permissions=['SPOT'],
            url='https://api.binance.com/api/v3/account'
        )

        accounts = BinanceAccount.objects.filter(user=curr_user, slug=slug)
        self.assertEqual(len(accounts), 1)
        self.assertEqual(slug, binance_account.slug)
        self.assertEqual(curr_user, binance_account.user)
        self.assertEqual(binance_account, accounts[0])
