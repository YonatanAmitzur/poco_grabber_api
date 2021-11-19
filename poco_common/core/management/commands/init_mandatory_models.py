"""
A Django management command to add the PoCo mandatory models if it doesn't already exist.
"""

from django.core.management.base import BaseCommand

from poco_common.exchange.exchange_actions.actions import ExchangeActions
from poco_common.core.models import SymbolInfo, BinanceAccount, GrabberSettings, GrabberSettingsRecords
from poco_common.core.utils.tools import get_system_user


class Command(BaseCommand, object):
    """
     Django management command to add the PoCo mandatory models if it doesn't already exist.
    """
    help = """ Django management command to add the PoCo mandatory models if it doesn't already exist."""

    def handle(self, *args, **options):
        """
        A Django management command to add the PoCo "system" user if it doesn't already exist.
        """
        exchange_actions = ExchangeActions()
        if SymbolInfo.objects.all().count() == 0:
            exchange_actions.update_trading_symbols_info()
            self.stdout.write("System init - trading_symbols_infos was successfully fetched.")
        if BinanceAccount.objects.all().count() == 0:
            exchange_actions.get_account_data(user=get_system_user())
            self.stdout.write("System init - binance account was successfully fetched.")
        if GrabberSettings.objects.all().count() == 0:
            instance = GrabberSettings.objects.create(
                user=get_system_user(),
                symbols=[],
                account_keys=[],
                state=GrabberSettings.STATE_INACTIVE
            )
            cloned_grabber_settings = {k: v for k, v in vars(instance).items() if k not in ('id', '_state')}
            GrabberSettingsRecords.objects.create(**dict(cloned_grabber_settings))
            cloned_grabber_settings['is_record_created'] = True
            self.stdout.write("System init - grabber_settings was successfully created.")
