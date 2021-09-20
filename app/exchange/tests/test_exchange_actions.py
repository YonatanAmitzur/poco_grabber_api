from django.test import TestCase
from django.contrib.auth import get_user_model

from exchange.exchange_actions.actions import ExchangeActions
from core.models import SymbolInfo


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
