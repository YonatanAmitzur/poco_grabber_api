from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import SymbolInfo
from exchange.serializers import SymbolInfoSerializer


SYMBOL_INFO_URL = reverse('data_grabber:symbolinfo-list')


class PublicSymbolInfoApiTests(TestCase):
    """Test the publicly available SymbolInfo API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving SymbolInfos"""
        res = self.client.get(SYMBOL_INFO_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateSymbolInfoApiTests(TestCase):
    """Test the authorized user SymbolInfo API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@poco.com',
            'password123',
            name='test'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_symbol_Info(self):
        """Test retrieving symbol info"""
        SymbolInfo.objects.create(
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

        SymbolInfo.objects.create(
            symbol='BNBBTC',
            status='TRADING',
            baseAsset='BNB',
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

        res = self.client.get(SYMBOL_INFO_URL)

        symbol_info_list = SymbolInfo.objects.all().order_by('-symbol')
        serializer = SymbolInfoSerializer(symbol_info_list, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_symbol_Info_by_symbol(self):
        """Test retrieving symbol info by symbol"""
        SymbolInfo.objects.create(
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

        SymbolInfo.objects.create(
            symbol='BNBBTC',
            status='TRADING',
            baseAsset='BNB',
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

        res = self.client.get(SYMBOL_INFO_URL, {'symbol': 'BNBBTC'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['symbol'], 'BNBBTC')

    def test_create_symbol_info_successful(self):
        """Test creating a new symbol info"""

        payload = {
            'symbol': 'ETHBTC',
            'status': 'TRADING',
            'baseAsset': 'ETH',
            'quoteAsset': 'BTC',
            'baseAssetPrecision': 8,
            'quotePrecision': 8,
            'quoteAssetPrecision': 8,
            'baseCommissionPrecision': 8,
            'quoteCommissionPrecision': 8,
            'orderTypes': ['LIMIT', 'LIMIT_MAKER', 'MARKET',
                           'STOP_LOSS_LIMIT', 'TAKE_PROFIT_LIMIT'],
            'icebergAllowed': True,
            'ocoAllowed': True,
            'quoteOrderQtyMarketAllowed': True,
            'isSpotTradingAllowed': True,
            'isMarginTradingAllowed': True,
            'filters': [
                {'filterType': 'PRICE_FILTER',
                 'minPrice': '0.00000100',
                 'maxPrice': '922327.00000000',
                 'tickSize': '0.00000100'},
                {'filterType': 'PERCENT_PRICE',
                 'multiplicerUp': '5',
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
                 'maxNumAlgoOrders': 5}
            ],
            'permissions': ['SPOT', 'MARGIN']
        }

        self.client.post(SYMBOL_INFO_URL, payload)

        exists = SymbolInfo.objects.filter(
            symbol=payload['symbol']
        ).exists()
        self.assertTrue(exists)

    def test_create_symbol_info_invalid(self):
        """Test creating a new symbol info with invalid payload"""
        payload = {
            'symbol': '',
        }
        res = self.client.post(SYMBOL_INFO_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
