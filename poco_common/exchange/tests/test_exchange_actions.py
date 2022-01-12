import time

from django.test import TestCase
from django.contrib.auth import get_user_model

from poco_common.exchange.exchange_actions.actions import ExchangeActions
from poco_common.core.models import SymbolInfo, SymbolEarliestTimestamp, BinanceAccountStatus


class ExchangeActionsTests(TestCase):
    """Test the exchange actions"""

    def test_get_trading_symbols_info_all(self):
        """Test get_trading_symbols_info func"""
        exchange_actions = ExchangeActions()
        symbols_info = exchange_actions.get_trading_symbols_info()
        self.assertIsNotNone(symbols_info)
        self.assertGreater(len(symbols_info), 0)

    def test_update_trading_symbols_info_all(self):
        """Test get_trading_symbols_info func"""
        exchange_actions = ExchangeActions()
        symbols_infos = exchange_actions.update_trading_symbols_info()
        symbols_list = [*(map(lambda o: o.symbol, symbols_infos))]
        self.assertIsNotNone(symbols_infos)
        self.assertGreater(len(symbols_infos), 0)
        symbol_info_list = SymbolInfo.objects.all()
        symbol_info_list_filter = symbol_info_list.filter(symbol__in=symbols_list)
        self.assertEqual(len(symbol_info_list_filter), len(symbols_list))

        symbols_infos = exchange_actions.update_trading_symbols_info()
        symbols_list = [*(map(lambda o: o.symbol, symbols_infos))]
        self.assertIsNotNone(symbols_infos)
        self.assertGreater(len(symbols_infos), 0)
        symbol_info_list = SymbolInfo.objects.all()
        symbol_info_list_filter = symbol_info_list.filter(symbol__in=symbols_list)
        self.assertEqual(len(symbol_info_list_filter), len(symbols_list))

    def test_get_trading_symbols_info_for_specific_quote_assets(self):
        """Test get_trading_symbols_info func"""
        exchange_actions = ExchangeActions()
        symbols_info = exchange_actions.get_trading_symbols_info(quote_assets=['ETH', 'ADA'])
        self.assertIsNotNone(symbols_info)
        self.assertGreater(len(symbols_info), 0)

    def test_update_trading_symbols_info_for_specific_quote_assets(self):
        """Test get_trading_symbols_info func"""
        exchange_actions = ExchangeActions()
        symbols_info = exchange_actions.update_trading_symbols_info(quote_assets=['ETH', 'ADA'])
        symbols_list = [*(map(lambda o: o.symbol, symbols_info))]
        self.assertIsNotNone(symbols_info)
        self.assertGreater(len(symbols_info), 0)
        symbol_info_list = SymbolInfo.objects.all()
        symbol_info_list_filter = symbol_info_list.filter(symbol__in=symbols_list)
        self.assertEqual(len(symbol_info_list_filter), len(symbols_list))

        symbols_info = exchange_actions.update_trading_symbols_info(quote_assets=['ETH', 'ADA'])
        symbols_list = [*(map(lambda o: o.symbol, symbols_info))]
        self.assertIsNotNone(symbols_info)
        self.assertGreater(len(symbols_info), 0)
        symbol_info_list = SymbolInfo.objects.all()
        symbol_info_list_filter = symbol_info_list.filter(symbol__in=symbols_list)
        self.assertEqual(len(symbol_info_list_filter), len(symbols_list))

    def test_get_trading_symbols_info_for_specific_symbols(self):
        """Test get_trading_symbols_info func"""
        exchange_actions = ExchangeActions()
        symbols_info = exchange_actions.get_trading_symbols_info(
            symbol_list=['ETHBTC', 'ADABTC'])
        self.assertIsNotNone(symbols_info)
        self.assertGreater(len(symbols_info), 0)
        self.assertEqual(len(symbols_info), 2)

    def test_update_trading_symbols_info_for_specific_symbols(self):
        """Test get_trading_symbols_info func"""
        exchange_actions = ExchangeActions()
        symbols_info = exchange_actions.update_trading_symbols_info(
            symbol_list=['ETHBTC', 'ADABTC'])
        symbols_list = [*(map(lambda o: o.symbol, symbols_info))]
        self.assertIsNotNone(symbols_info)
        self.assertGreater(len(symbols_info), 0)
        symbol_info_list = SymbolInfo.objects.all()
        symbol_info_list_filter = symbol_info_list.filter(symbol__in=symbols_list)
        self.assertEqual(len(symbol_info_list_filter), len(symbols_list))
        self.assertEqual(len(symbols_info), 2)

        symbols_info = exchange_actions.update_trading_symbols_info(
            symbol_list=['ETHBTC', 'ADABTC'])
        symbols_list = [*(map(lambda o: o.symbol, symbols_info))]
        self.assertIsNotNone(symbols_info)
        self.assertGreater(len(symbols_info), 0)
        symbol_info_list = SymbolInfo.objects.all()
        symbol_info_list_filter = symbol_info_list.filter(symbol__in=symbols_list)
        self.assertEqual(len(symbol_info_list_filter), len(symbols_list))
        self.assertEqual(len(symbols_info), 2)

    def test_get_account_data(self):
        """Test get_account_data func"""
        user = get_user_model().objects.create_user(
            email='test@poco.com',
            password='testpass',
            name='test'
        )

        exchange_actions = ExchangeActions()
        account_data = exchange_actions.get_account_data(user=user)

        self.assertIsNotNone(account_data)
        self.assertEqual(user, account_data['user'])
        self.assertGreater(len(account_data['balances']), 0)

    def test_get_binance_ping(self):
        """Test get_binance_ping func - getting ping from binance"""

        exchange_actions = ExchangeActions()
        res = exchange_actions.get_binance_ping()
        self.assertIsNotNone(res)
        self.assertEqual(res, {})

    def test_get_earliest_valid_timestamp_for_spot(self):
        """Test get_binance_ping func - getting ping from binance"""

        user = get_user_model().objects.create_user(
            email='test@poco.com',
            password='testpass',
            name='test'
        )

        exchange_actions = ExchangeActions()
        res = exchange_actions.get_earliest_valid_timestamp_for_spot(symbol='BTCUSDT', interval='1d', user=user)
        self.assertEqual(type(res), SymbolEarliestTimestamp)
        self.assertEqual(res.symbol, 'BTCUSDT')
        self.assertEqual(res.interval, '1d')
        self.assertEqual(res.user, user)
        self.assertIsNotNone(res.earliest_datetime)
        self.assertIsNotNone(res.earliest_timestamp)
        self.assertIsNotNone(res.created)
        self.assertIsNotNone(res.updated)

        symbol_earliest_recs = SymbolEarliestTimestamp.objects.filter(user=user, symbol='BTCUSDT', interval='1d')
        self.assertEqual(symbol_earliest_recs.count(), 1)

        res2 = exchange_actions.get_earliest_valid_timestamp_for_spot(symbol='BTCUSDT', interval='1d', user=user)
        self.assertEqual(res.earliest_timestamp, res.earliest_timestamp)
        self.assertEqual(res2.earliest_datetime, res.earliest_datetime)
        self.assertIsNotNone(res2.created)
        self.assertIsNotNone(res2.updated)
        symbol_earliest_recs = SymbolEarliestTimestamp.objects.filter(user=user, symbol='BTCUSDT', interval='1d')
        self.assertEqual(symbol_earliest_recs.count(), 1)

    def test_get_account_status(self):
        """Test get_account_status func - getting check if account status is normal"""

        user = get_user_model().objects.create_user(
            email='test@poco.com',
            password='testpass',
            name='test'
        )

        exchange_actions = ExchangeActions()
        res = exchange_actions.get_account_status(user=user)
        self.assertIsNotNone(res)
        self.assertEqual(type(res), BinanceAccountStatus)
        self.assertEqual(res.status, 'Normal')
        binance_account_status = BinanceAccountStatus.objects.get(slug=res.slug)
        self.assertEqual(binance_account_status.user, res.user)
        self.assertEqual(binance_account_status.created, res.created)
        self.assertEqual(binance_account_status.status, res.status)

    def test_get_all_coins_info(self):
        """Test get_all_coins_info func"""

        user = get_user_model().objects.create_user(
            email='test@poco.com',
            password='testpass',
            name='test'
        )

        exchange_actions = ExchangeActions()
        all_coins_info_data = exchange_actions.get_all_coins_info(user=user)
        self.assertIsNotNone(all_coins_info_data)
        self.assertEqual(user, all_coins_info_data[0]['user'])
        self.assertTrue(len(all_coins_info_data) > 0)

