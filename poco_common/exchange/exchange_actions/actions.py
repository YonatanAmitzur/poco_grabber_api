from datetime import datetime, timezone

from poco_common.exchange.binance_source.python_binance.client import Client
from poco_common.exchange.binance_source.python_binance.enums_ext import STATUS_TRADING

from poco_common.exchange.exchange_exceptions.exceptions import DuplicatedSymbolException, \
    BinanceException, MoreThanOneBinanceAccountException
from poco_common.core.models import SymbolInfo, BinanceAccount, SymbolEarliestTimestamp, \
    BinanceAccountStatus, CoinInfo
from poco_common.exchange.serializers import SymbolInfoSerializer, BinanceAccountSerializer, \
    CoinInfoSerializer
from poco_common.exchange.binance_source.python_binance.exceptions import BinanceAPIException, BinanceRequestException
from poco_common.core.core_exceptions.general_exceptions import DbIntegrityException


class ExchangeActions:

    def __init__(self, filename='credentials.txt'):

        if filename is None:
            return

        f = open(__file__.replace('exchange_actions/actions.py', 'binance_source/' + filename),
                 "r")
        contents = []
        if f.mode == 'r':
            contents = f.read().split('\n')

        api_key = contents[0]
        secret_key = contents[1]

        self.client = Client(api_key, secret_key)

    def get_trading_symbols_info_raw(self,
                                     quote_assets: list = [],
                                     symbol_list: list = []):
        symbols = []
        try:
            exchange_info = self.client.get_exchange_info()

            if len(symbol_list) == 0 and len(quote_assets) == 0:
                for item in exchange_info['symbols']:
                    if item['status'] == STATUS_TRADING:
                        symbols.append(item)

            if len(symbol_list) > 0 or len(quote_assets) > 0:
                for item in exchange_info['symbols']:
                    if item['status'] == STATUS_TRADING and \
                            (item['symbol'] in symbol_list or item['quoteAsset'] in quote_assets):
                        symbols.append(item)
        except Exception as ex:
            raise BinanceException(message=ex)

        return symbols

    def get_trading_symbols_info(self,
                                 quote_assets: list = [],
                                 symbol_list: list = []):
        results = []
        symbols = self.get_trading_symbols_info_raw(quote_assets=quote_assets,
                                                    symbol_list=symbol_list)
        for item in symbols:
            serializer = SymbolInfoSerializer(data=item)
            serializer.is_valid()
            results.append(serializer.validated_data)

        return results

    def update_trading_symbols_info(self,
                                    quote_assets: list = [],
                                    symbol_list: list = []):
        results_symbols = []
        symbols = self.get_trading_symbols_info_raw(quote_assets=quote_assets,
                                                    symbol_list=symbol_list)

        for item in symbols:
            serializer = SymbolInfoSerializer(data=item)
            serializer.is_valid()

            symbol = item['symbol']
            results_symbols.append(symbol)
            symbols_info = SymbolInfo.objects.filter(symbol=symbol)
            if len(symbols_info) == 0:
                serializer.save()
            else:
                if len(symbols_info) > 1:
                    raise DuplicatedSymbolException(message=symbol)

                symbol_info = symbols_info[0]
                serializer.update(symbol_info, serializer.validated_data)
        return SymbolInfo.objects.filter(symbol__in=results_symbols)

    def get_account_data(self, user):
        try:
            account_data = self.client.get_account()
        except Exception as ex:
            raise BinanceException(message=ex)

        account_data['user'] = user.id
        serializer = BinanceAccountSerializer(data=account_data)
        serializer.is_valid()
        return serializer.validated_data

    def update_account_data(self, user):
        try:
            account_data = self.client.get_account()
        except Exception as ex:
            raise BinanceException(message=ex)

        serializer = BinanceAccountSerializer(data=account_data)
        serializer.is_valid()

        binance_account = BinanceAccount.objects.filter(user=user)
        if len(binance_account) == 0:
            binance_account.user = user
            saved_account = serializer.save()
            return saved_account
        else:
            if len(binance_account) > 1:
                raise MoreThanOneBinanceAccountException(message=user)

            serializer.update(binance_account, serializer.validated_data)
            return serializer.validated_data

    def get_earliest_valid_timestamp_for_spot(self, symbol, interval, user):
        try:
            timestamp = self.client._get_earliest_valid_timestamp(symbol=symbol, interval=interval)
            existed_records = SymbolEarliestTimestamp.objects.filter(user=user, symbol=symbol, interval=interval)
            if timestamp and timestamp > 0:
                if existed_records.count() > 0:
                    if timestamp == existed_records[0].earliest_timestamp:
                        return existed_records[0]
                    existed_records.update(
                        earliest_timestamp=timestamp,
                        earliest_datetime=datetime.fromtimestamp(float(timestamp/1000), timezone.utc))
                    res = SymbolEarliestTimestamp.objects.get(user=user, symbol=symbol, interval=interval)
                else:
                    res = SymbolEarliestTimestamp.objects.create(user=user, symbol=symbol, earliest_timestamp=timestamp,
                                                                 interval=interval, earliest_datetime=
                                                                 datetime.fromtimestamp(float(timestamp/1000),
                                                                                        timezone.utc))
            else:
                raise BinanceException(message='invalid earliest valid timestamp')
        except Exception as ex:
            raise BinanceException(message=ex)
        return res

    def get_binance_ping(self):
        try:
            res = self.client.ping()
        except BinanceRequestException as ex:
            # TODO: send to sentry
            print(ex)
        except BinanceAPIException as ex:
            # TODO: send to sentry
            print(ex)
        except Exception as ex:
            raise BinanceException(message=ex)
        return res

    def get_account_status(self, user):
        try:
            res = self.client.get_account_status()
            if res and 'data' in dict(res).keys():
                binance_account_status = BinanceAccountStatus.objects.create(
                    user=user,
                    status=dict(res)['data']
                )
                return binance_account_status
            else:
                raise BinanceException(message='invalid binance account status')
        except Exception as ex:
            raise BinanceException(message=ex)

    def get_all_coins_info(self, user):
        try:
            all_coins_info = self.client.get_all_coins_info()
        except Exception as ex:
            raise BinanceException(message=ex)

        res_all_coins_infos = []

        for coin_info in all_coins_info:
            coin_info['user'] = user.id
            serializer = CoinInfoSerializer(data=coin_info)
            serializer.is_valid()
            res_all_coins_infos.append(serializer.validated_data)
        return res_all_coins_infos

    def update_all_coins_info(self, user):
        all_coins_infos = self.get_all_coins_info(user)
        for coin_info in all_coins_infos:
            serializer = SymbolInfoSerializer(data=coin_info)
            serializer.is_valid()
            existed_coins = CoinInfo.objects.filter(coin=serializer.validated_data['coin'])
            if existed_coins.count() > 1:
                raise DbIntegrityException(message="more than one coin_info record exist with the same coin value")
            if existed_coins.count() == 1:
                existed_coin = existed_coins[0]
                serializer.update(existed_coin, serializer.validated_data)
            else:
                serializer.save(serializer.validated_data)

