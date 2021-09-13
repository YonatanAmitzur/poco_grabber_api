from core.models import GrabberRun, LooperSettings
from exchange.exchange_actions.actions import ExchangeActions
from multiprocessing.pool import ThreadPool as Pool


class Looper:

    def __init__(self, grabber):
        self.grabber = grabber
        self.exchange_actions = ExchangeActions()
        self.looper_settings = LooperSettings.load()

    def run(self):
        num_of_threads = 4
        user_multi_threading = True

        if self.looper_settings.run_type == LooperSettings.RUN_TYPE_UPDATE_SYMBOLS_ONLY or \
                self.looper_settings.run_type == LooperSettings.RUN_TYPE_UPDATE_PAIRS_ONLY or \
                self.looper_settings.run_type == LooperSettings.RUN_TYPE_UPDATE_PAIRS_ONLY:
            user_multi_threading = False

        self.grabber.status = GrabberRun.STATUS_ACTIVE
        self.grabber.save()

        if user_multi_threading:
            pool = Pool(num_of_threads)
            # func1 = partial(self.EntryOrder, bot_params, strategy_function, pairs)
            # pool.map(func1, symbol_datas)
            pool.close()
            pool.join()
        else:
            if self.looper_settings.run_type == LooperSettings.RUN_TYPE_UPDATE_SYMBOLS_ONLY:
                self.exchange_actions.update_trading_symbols_info()

        self.grabber.status = GrabberRun.STATUS_INACTIVE
        self.grabber.save()
