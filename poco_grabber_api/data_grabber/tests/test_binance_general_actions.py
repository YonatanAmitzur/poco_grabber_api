from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from unittest.mock import patch, MagicMock

from rest_framework import status
from rest_framework.test import APIClient

from poco_common.exchange.exchange_actions.actions import ExchangeActions
from poco_common.exchange.binance_source.python_binance.exceptions import BinanceAPIException, \
    BinanceRequestException
from poco_common.core.models import BinanceAccountStatus


BINANCE_GENERAL_ACTION_PING = reverse('data_grabber:binance_actions-ping-binance')


class PublicBinanceGeneralActionsApiTests(TestCase):
    """Test the publicly available BinanceGeneralActions API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving SymbolInfos"""
        res = self.client.get(BINANCE_GENERAL_ACTION_PING)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBinanceGeneralActionsApiTests(TestCase):
    """Test the authorized user BinanceGeneralActions API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@poco.com',
            'password123',
            name='test'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_ping_binance(self):
        """Test pinging binance"""

        res = self.client.get(BINANCE_GENERAL_ACTION_PING)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.content.decode("utf-8"), '"ok"')

    def test_ping_binance_fail_return_none(self):
        """Test pinging binance"""

        with patch.object(ExchangeActions, 'get_binance_ping', return_value=None) as mock_method:
            res = self.client.get(BINANCE_GENERAL_ACTION_PING)
        mock_method.assert_called_once()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.json()['error'], 'error with no exception')

    def test_ping_binance_fail_raise_binance_api_exception(self):
        """Test pinging binance"""

        with patch.object(ExchangeActions, 'get_binance_ping') as mock_method:
            object_with_test_attr = MagicMock(text='error')
            mock_method.side_effect = BinanceAPIException(response=object_with_test_attr,
                                                          status_code=400,
                                                          text="{'code': '400', 'msg': 'error'}")
            res = self.client.get(BINANCE_GENERAL_ACTION_PING)
        mock_method.assert_called_once()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.json()['error'],
                         'APIError(code=0): Invalid JSON error message from Binance: error')

    def test_ping_binance_fail_raise_binance_request_exception(self):
        """Test pinging binance"""

        with patch.object(ExchangeActions, 'get_binance_ping') as mock_method:
            mock_method.side_effect = BinanceRequestException(message="error")
            res = self.client.get(BINANCE_GENERAL_ACTION_PING)
        mock_method.assert_called_once()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.json()['error'], 'BinanceRequestException: error')

    def test_account_status(self):
        """Test getting binance account status"""

        res = self.client.get(reverse('data_grabber:binance_actions-account-status',
                                      args=[self.user.slug]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res_data = res.json()
        binance_account_status = BinanceAccountStatus.objects.get(slug=res_data['slug'])
        self.assertEqual(binance_account_status.created.isoformat()
                         .replace('+00:00', 'Z'), res_data['created'])
        self.assertEqual(binance_account_status.status, res_data['status'])
        self.assertEqual(binance_account_status.user.slug, res_data['user_slug'])
