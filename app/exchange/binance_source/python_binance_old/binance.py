import requests
import json
import decimal
import hmac
import time
import pandas as pd
import hashlib
from decimal import Decimal
from uuid import uuid1

request_delay = 1000


class Binance:
    ORDER_STATUS_NEW = 'NEW'
    ORDER_STATUS_PARTIALLY_FILLED = 'PARTIALLY_FILLED'
    ORDER_STATUS_FILLED = 'FILLED'
    ORDER_STATUS_CANCELED = 'CANCELED'
    ORDER_STATUS_PENDING_CANCEL = 'PENDING_CANCEL'
    ORDER_STATUS_REJECTED = 'REJECTED'
    ORDER_STATUS_EXPIRED = 'EXPIRED'

    SIDE_BUY = 'BUY'
    SIDE_SELL = 'SELL'

    STATUS_TRADING = 'TRADING'

    ORDER_TYPE_LIMIT = 'LIMIT'
    ORDER_TYPE_MARKET = 'MARKET'
    ORDER_TYPE_STOP_LOSS = 'STOP_LOSS'
    ORDER_TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
    ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
    ORDER_TYPE_TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
    ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER'

    KLINE_INTERVALS = ['1m', '3m', '5m', '15m', '30m', '1h',
                       '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']

    def __init__(self, filename='credentials.txt'):

        self.base = 'https://api.binance.com'

        self.endpoints = {
            "order": '/api/v3/order/test',
            "orderOco": '/api/v3/order/oco/test',
            "testOrder": '/api/v3/order/test',
            "allOrders": '/api/v3/allOrders',
            "klines": '/api/v3/klines',
            "exchangeInfo": '/api/v3/exchangeInfo',
            "24hrTicker": '/api/v3/ticker/24hr',
            "averagePrice": '/api/v3/avgPrice',
            "orderBook": '/api/v3/depth',
            "account": '/api/v3/account',
            "allOpenOrders": '/api/v3/openOrders',
            "priceTicker": '/api/v3/ticker/price',
            "orderListOco": '/api/v3/orderList'
        }
        self.account_access = False

        if filename is None:
            return

        f = open(__file__.replace('binance.py', filename), "r")
        contents = []
        if f.mode == 'r':
            contents = f.read().split('\n')

        self.binance_keys = dict(api_key=contents[0], secret_key=contents[1])
        self.headers = {"X-MBX-APIKEY": self.binance_keys['api_key']}
        self.account_access = True

    def _get(self, url, params=None, headers=None) -> dict:
        try:
            response = requests.get(url, params=params, headers=headers)
            data = {}
            if response.text and response.text.startswith('[') and response.text.endswith(']'):
                data['data'] = json.loads(response.text)
                data['url'] = url
            else:
                data = json.loads(response.text)
                data['url'] = url
        except Exception as e:
            print("Exception occured when trying to access " + url)
            print(e)
            data = {'code': '-1', 'url': url, 'msg': e}
        return data

    def _post(self, url, params=None, headers=None) -> dict:
        try:
            response = requests.post(url, params=params, headers=headers)
            data = json.loads(response.text)
            data['url'] = url
        except Exception as e:
            print("Exception occured when trying to access " + url)
            print(e)
            data = {'code': '-1', 'url': url, 'msg': e}
        return data

    def sign_request(self, params: dict):
        ''' Signs the request to the Binance API '''

        query_string = '&'.join(["{}={}".format(d, params[d]) for d in params])
        signature = \
            hmac.new(self.binance_keys['secret_key'].encode('utf-8'), query_string.encode('utf-8'),
                     hashlib.sha256)
        params['signature'] = signature.hexdigest()

    def get_trading_symbols_info(self, quote_assets: list = None, symbol_list: list = None):
        url = self.base + self.endpoints["exchangeInfo"]
        data = self._get(url)
        if data.__contains__('code'):
            return []

        symbols_list = []
        for pair in data['symbols']:
            if pair['status'] == self.STATUS_TRADING:
                if quote_assets is None and symbol_list is None:
                    symbols_list.append(pair)
                else:
                    if (quote_assets is not None and pair['quoteAsset'] in quote_assets) \
                                or (symbol_list is not None and pair['symbol'] in symbol_list):
                        symbols_list.append(pair)

        return symbols_list

    def get_symbol_data_by_symbol_list(self, symbols: list = None):
        return self.get_trading_symbols_info(symbol_list=symbols)

    def get_symbol_data_by_quote_assets(self, quote_assets: list = None):
        return self.get_trading_symbols_info(quote_assets=quote_assets)

    def get_trading_symbols(self, quote_assets: list = None, symbol_list: list = None):
        symbols_infos = self.get_trading_symbols_info(quote_assets=quote_assets,
                                                      symbol_list=symbol_list)
        symbols_list = [*(map(lambda o: o.symbol, symbols_infos))]
        return symbols_list

    # No unit test from here
    def get_account_data(self) -> dict:
        url = self.base + self.endpoints["account"]

        params = {
            'recvWindow': 6000,
            'timestamp': int(round(time.time() * 1000)) + request_delay
        }
        self.sign_request(params)

        return self._get(url, params, self.headers)

    def get_symbol_k_lines_extra(self, symbol: str,
                                 interval: str,
                                 limit: int = 1000,
                                 end_time=False):
        repeat_rounds = 0
        if limit > 1000:
            repeat_rounds = int(limit / 1000)
        initial_limit = limit % 1000
        if initial_limit == 0:
            initial_limit = 1000
        # First, we get the last initial_limit candles, starting at end_time and going
        # backwards (or starting in the present moment, if end_time is False)
        df = self.GetSymbolKlines(symbol, interval, limit=initial_limit, end_time=end_time)
        while repeat_rounds > 0:
            # Then, for every other 1000 candles, we get them, but starting at the beginning
            # of the previously received candles.
            df2 = self.GetSymbolKlines(symbol, interval, limit=1000, end_time=df['time'][0])
            df = df2.append(df, ignore_index=True)
            repeat_rounds = repeat_rounds - 1

        return df

    def get_24hr_ticker(self, symbol: str):
        url = self.base + self.endpoints['24hrTicker'] + "?symbol=" + symbol
        return self._get(url)

    def get_price_ticker(self, symbol: str):
        url = self.base + self.endpoints['priceTicker'] + "?symbol=" + symbol
        return self._get(url)

    def get_symbol_k_lines(self, symbol: str, interval: str, limit: int = 1000, end_time=False):
        if limit > 1000:
            return self.GetSymbolKlinesExtra(symbol, interval, limit, end_time)

        params = '?&symbol=' + symbol + '&interval=' + interval + '&limit=' + str(limit)
        if end_time:
            params = params + '&endTime=' + str(int(end_time))

        url = self.base + self.endpoints['klines'] + params

        # download data
        data = requests.get(url)
        dictionary = json.loads(data.text)

        # put in dataframe and clean-up
        df = pd.DataFrame.from_dict(dictionary)
        df = df.drop(range(6, 12), axis=1)

        # rename columns
        col_names = ['time', 'open', 'high', 'low', 'close', 'volume']
        df.columns = col_names

        # transform values from strings to floats
        for col in col_names:
            df[col] = df[col].astype(float)

        df['date'] = pd.to_datetime(df['time'] * 1000000, infer_datetime_format=True)

        return df

    def place_order_from_dict(self, params, test: bool = False):
        params['recvWindow'] = 5000
        params['timestamp'] = int(round(time.time() * 1000)) + request_delay

        self.sign_request(params)
        url = ''
        if test:
            url = self.base + self.endpoints['testOrder']
        else:
            url = self.base + self.endpoints['order']
        return self._post(url, params, self.headers)

    def place_oco_order_from_dict(self, params, test: bool = False):
        params['recvWindow'] = 5000
        params['timestamp'] = int(round(time.time() * 1000)) + request_delay

        self.sign_request(params)
        url = ''
        if test:
            url = self.base + self.endpoints['testOrder']
        else:
            url = self.base + self.endpoints['orderOco']
        return self._post(url, params, self.headers)

    def place_order(self, symbol: str, side: str, type: str,
                    quantity: float = 0, price: float = 0, test: bool = True):
        params = {
            'symbol': symbol,
            'side': side,  # BUY or SELL
            'type': type,  # MARKET, LIMIT, STOP LOSS etc
            'quoteOrderQty': quantity,
            'recvWindow': 5000,
            'timestamp': int(round(time.time() * 1000)) + request_delay
        }

        if type != 'MARKET':
            params['timeInForce'] = 'GTC'
            params['price'] = Binance.float_to_string(price)

        self.sign_request(params)

        url = ''
        if test:
            url = self.base + self.endpoints['testOrder']
        else:
            url = self.base + self.endpoints['order']

        return self._post(url, params=params, headers=self.headers)

    def cancel_order(self, symbol: str, orderId: str):
        params = {
            'symbol': symbol,
            'origClientOrderId': orderId,
            'recvWindow': 5000,
            'timestamp': int(round(time.time() * 1000)) + request_delay
        }

        self.sign_request(params)

        url = self.base + self.endpoints['order']

        try:
            response = requests.delete(url, params=params, headers=self.headers)
            data = response.text
        except Exception as e:
            print("Exception occured when trying to cancel order on " + url)
            print(e)
            data = {'code': '-1', 'msg': e}

        return json.loads(data)

    def cancel_oco_order(self, symbol: str, orderListId: str):
        params = {
            'symbol': symbol,
            'orderListId': orderListId,
            'recvWindow': 5000,
            'timestamp': int(round(time.time() * 1000)) + request_delay
        }

        self.sign_request(params)

        url = self.base + self.endpoints['orderListOco']

        try:
            response = requests.delete(url, params=params, headers=self.headers)
            data = response.text
        except Exception as e:
            print("Exception occured when trying to cancel oco order on " + url)
            print(e)
            data = {'code': '-1', 'msg': e}

        return json.loads(data)

    def get_open_orders_symbol(self, symbol: str):
        params = {
            'symbol': symbol,
            'recvWindow': 5000,
            'timestamp': int(round(time.time() * 1000)) + request_delay
        }

        self.sign_request(params)

        url = self.base + self.endpoints['allOpenOrders']

        return self._get(url, params=params, headers=self.headers)

    def get_all_open_orders(self):
        params = {
            'recvWindow': 5000,
            'timestamp': int(round(time.time() * 1000)) + request_delay
        }

        self.sign_request(params)

        url = self.base + self.endpoints['allOpenOrders']

        return self._get(url, params=params, headers=self.headers)

    def order_list_oco(self, orderListId: int):
        params = {
            'orderListId': orderListId,
            'recvWindow': 5000,
            'timestamp': int(round(time.time() * 1000)) + request_delay
        }

        self.sign_request(params)

        url = self.base + self.endpoints['orderListOco']

        return self._get(url, params=params, headers=self.headers)

    def get_order_info(self, symbol: str, orderId: str):
        params = {
            'symbol': symbol,
            'origClientOrderId': orderId,
            'recvWindow': 5000,
            'timestamp': int(round(time.time() * 1000)) + request_delay
        }

        self.sign_request(params)

        url = self.base + self.endpoints['order']

        return self._get(url, params=params, headers=self.headers)

    def top_up_bnb(self, min_balance: float, topup: float, buy_with: str, test_run: bool):
        account_data = self.GetAccountData()

        requested_times = 0
        while not self.GetAccountData():
            requested_times = requested_times + 1
            time.sleep(1)
            account_data = self.GetAccountData()
            if requested_times > 15:
                self.sp.stop()
                print("\nCan't get balance from exchange,"
                      " tried more than 15 times.\n", "Stopping.\n")
                return False

        list_of_items = account_data['balances']
        item = "BNB"
        pos = -1

        # Iterate over list items by index pos
        for i in range(len(list_of_items)):
            # Check if items matches the given element
            if list_of_items[i]["asset"] == item:
                pos = i
                break
        if pos == -1:
            print(f'Element "{item}" does not exist in the list: ', pos)
        # else:
        # print(f'Index of element "{item}" in the list is: ', pos)

        if pos == -1:
            return False

        bnb_balance = list_of_items[pos]
        bnb_balance_value = float(bnb_balance['free'])
        if bnb_balance_value < min_balance:
            qty = round(topup - bnb_balance_value, 5)
            # print(qty)
            order_id = str(uuid1())
            order_params = dict(
                symbol="BNB" + buy_with,
                side="BUY",
                type="MARKET",
                quantity=qty,
                newClientOrderId=order_id)

            order_result = self.PlaceOrderFromDict(order_params, test=test_run)

            if order_result is not False:
                return True

        return False

    def get_all_order_info(self, symbol: str):
        params = {
            'symbol': symbol,
            'timestamp': int(round(time.time() * 1000)) + request_delay
        }

        self.sign_request(params)

        url = self.base + self.endpoints['allOrders']

        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.text
        except Exception as e:
            print("Exception occured when trying to get info on all orders on " + url)
            print(e)
            data = {'code': '-1', 'msg': e}

        return json.loads(data)

    @classmethod
    def float_to_string(cls, f: float):
        ctx = decimal.Context()
        ctx.prec = 12
        d1 = ctx.create_decimal(repr(f))
        return format(d1, 'f')

    @classmethod
    def get_10_factor(cls, num):
        p = 0
        for i in range(-20, 20):
            if num == num % 10 ** i:
                p = -(i - 1)
                break
        return p

    @classmethod
    def round_to_valid_price(cls, symbol_data, desired_price, round_up: bool = False) -> Decimal:
        pr_filter = {}

        for fil in symbol_data["filters"]:
            if fil["filterType"] == "PRICE_FILTER":
                pr_filter = fil
                break

        if not pr_filter.keys().__contains__("tickSize"):
            raise Exception("Couldn't find tickSize or PRICE_FILTER in symbol_data.")
            return

        round_off_number = int(cls.get_10_factor((float(pr_filter["tickSize"]))))

        number = round(Decimal(desired_price), round_off_number)
        if round_up:
            number = number + Decimal(pr_filter["tickSize"])

        return number

    @classmethod
    def round_to_valid_quantity(cls, symbol_data, desired_quantity,
                                round_up: bool = False) -> Decimal:
        lot_filter = {}

        for fil in symbol_data["filters"]:
            if fil["filterType"] == "LOT_SIZE":
                lot_filter = fil
                break

        if not lot_filter.keys().__contains__("stepSize"):
            raise Exception("Couldn't find stepSize or PRICE_FILTER in symbol_data.")
            return

        round_off_number = int(cls.get_10_factor((float(lot_filter["stepSize"]))))

        # desired_quantity = desired_quantity - (desired_quantity * Decimal(0.001))
        number = round(Decimal(desired_quantity), round_off_number)
        if round_up:
            number = number + Decimal(lot_filter["stepSize"])

        return number
