class DuplicatedSymbolException(Exception):

    def __init__(self, message, **kwargs):
        self.reason = "duplicated_symbol_in_internal_db"
        self.extra = kwargs
        msg = f"Duplicated symbol in internal db, symbol={message}"
        super(DuplicatedSymbolException, self).__init__(msg)


class BinanceException(Exception):

    def __init__(self, message, **kwargs):
        self.reason = "binance_exception"
        self.extra = kwargs
        msg = f"Binance exception, message={message}"
        super(BinanceException, self).__init__(msg)


class MoreThanOneBinanceAccountException(Exception):

    def __init__(self, message, **kwargs):
        self.reason = "user_has_more_than_one_binance_account"
        self.extra = kwargs
        msg = f"u" \
              f"User has more than one binance account, symbol={message}"
        super(DuplicatedSymbolException, self).__init__(msg)
