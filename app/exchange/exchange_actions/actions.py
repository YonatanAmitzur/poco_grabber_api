from exchange.binance_source.python_binance.client import Client
from exchange.binance_source.python_binance.enums_ext import STATUS_TRADING

from exchange.exchange_exceptions.exceptions import DuplicatedSymbolException, \
    BinanceException, MoreThanOneBinanceAccountException
from core.models import SymbolInfo, BinanceAccount
from exchange.serializers import SymbolInfoSerializer, BinanceAccountSerializer


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
