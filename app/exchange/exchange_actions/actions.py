from exchange.binance_source.binance import Binance
from core.models import SymbolInfo
from exchange.serializers import SymbolInfoSerializer


class ExchangeActions:

    def __init__(self):
        self.exchange = Binance()

    def get_trading_symbols_info(self):
        return self.exchange.get_trading_symbols_info()

    def update_trading_symbols_info(self):
        results = self.get_trading_symbols_info()
        for item in results:
            serializer = SymbolInfoSerializer(data=item)
            serializer.is_valid()

            symbol = item['symbol']
            symbol_info = SymbolInfo.objects.get(symbol)
            if symbol_info is None:
                serializer.save()
            else:
                serializer.update(symbol_info, serializer.validated_data)

    def get_account_data(self):
        pass

    def update_account_data(self):
        pass
