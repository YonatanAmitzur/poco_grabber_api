from django.core.exceptions import PermissionDenied

from exchange.binance_source.binance import Binance
from exchange.exchange_exceptions.exceptions import DuplicatedSymbolException, \
    BinanceException, MoreThanOneBinanceAccountException
from core.models import SymbolInfo, BinanceAccount
from exchange.serializers import SymbolInfoSerializer, BinanceAccountSerializer


class ExchangeActions:

    def __init__(self):
        self.exchange = Binance()

    def get_trading_symbols_info(self,
                                 quote_assets: list = None,
                                 symbol_list: list = None):
        symbols = []
        try:
            results = self.exchange.get_trading_symbols_info(quote_assets=quote_assets,
                                                             symbol_list=symbol_list)
        except Exception as ex:
            raise BinanceException(message=ex)

        for item in results:
            serializer = SymbolInfoSerializer(data=item)
            serializer.is_valid()
            symbols.append(serializer.validated_data)
        return symbols

    def update_trading_symbols_info(self,
                                    quote_assets: list = None,
                                    symbol_list: list = None):
        symbols = []

        try:
            results = self.exchange.get_trading_symbols_info(quote_assets=quote_assets,
                                                             symbol_list=symbol_list)
        except Exception as ex:
            raise BinanceException(message=ex)

        for item in results:
            serializer = SymbolInfoSerializer(data=item)
            serializer.is_valid()

            symbol = item['symbol']
            symbols.append(symbol)
            symbol_infos = SymbolInfo.objects.filter(symbol=symbol)
            if len(symbol_infos) == 0:
                serializer.save()
            else:
                if len(symbol_infos) > 1:
                    raise DuplicatedSymbolException(message=symbol)

                symbol_info = symbol_infos[0]
                serializer.update(symbol_info, serializer.validated_data)
        return SymbolInfo.objects.filter(symbol__in=symbols)

    def get_account_data(self, user):
        try:
            account_data = self.exchange.get_account_data()
        except Exception as ex:
            raise BinanceException(message=ex)

        account_data['user'] = user.id
        serializer = BinanceAccountSerializer(data=account_data)
        serializer.is_valid()
        return serializer.validated_data

    def update_account_data(self, user):
        try:
            account_data = self.exchange.get_account_data()
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
