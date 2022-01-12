import uuid
from django.db import models
from django.core.cache import cache
from django.db.models import PositiveIntegerField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.db.models import signals
from django.dispatch import receiver

from poco_common.core.utils import validators


def make_slug():
    return uuid.uuid4().hex


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)

        # try:
        #     user.full_clean()
        # except ValidationError as ex:
        #     import ipdb;ipdb.set_trace()
        #     # Do something when validation is not passing
        #     raise ex
        # else:
        #     # Validation is ok we will save the instance
        #     user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        extra_fields = {'name': 'super_user'}
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that suppors using email instead of username"""
    USERNAME_FIELD = 'email'

    ENTERPRISE = 'enterprise'
    SMB = 'smb'
    STANDARD = 'standard'
    TIER_CHOICES = (
        (ENTERPRISE, 'enterprise'),
        (SMB, 'smb'),
        (STANDARD, 'standard'),
    )

    USER_TYPE_GRABBER = 'GRABBER'
    USER_TYPE_TRADER = 'TRADER'
    USER_TYPE_GRABBER_AND_TRADER = 'GRABBER_AND_TRADER'
    USER_TYPE_CHOICES = (
        (USER_TYPE_GRABBER, 'GRABBER'),
        (USER_TYPE_TRADER, 'TRADER'),
        (USER_TYPE_GRABBER_AND_TRADER, 'GRABBER_AND_TRADER'),
    )

    STATUS_ACTIVE = 'ACTIVE'
    STATUS_APPLIED = 'APPLIED'
    STATUS_APPROVED = 'APPROVED'
    STATUS_CANCELED = 'CANCELED'
    STATUS_CREATED = 'CREATED'
    STATUS_DEFAULT = 'DEFAULT'
    STATUS_INACTIVE = 'INACTIVE'
    STATUS_REJECTED = 'REJECTED'
    STATUS_SUSPENDED = 'SUSPENDED'
    STATUS_UNQUALIFIED = 'UNQUALIFIED'
    STATUS_CHOICES = (
        (STATUS_ACTIVE, 'ACTIVE'),
        (STATUS_APPLIED, 'APPLIED'),
        (STATUS_APPROVED, 'APPROVED'),
        (STATUS_CANCELED, 'CANCELED'),
        (STATUS_CREATED, 'CREATED'),
        (STATUS_DEFAULT, 'DEFAULT'),
        (STATUS_INACTIVE, 'INACTIVE'),
        (STATUS_REJECTED, 'REJECTED'),
        (STATUS_SUSPENDED, 'SUSPENDED'),
        (STATUS_UNQUALIFIED, 'UNQUALIFIED'),
    )

    created_by_user_id = PositiveIntegerField(null=True, blank=True)
    updated_by_user_id = PositiveIntegerField(null=True, blank=True)
    slug = models.CharField(max_length=32, unique=False, default=make_slug, db_index=True)
    email = models.EmailField(
        unique=True,
        db_index=True,
        max_length=254,
        validators=[validators.email, validators.lower_case],
    )
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.TextField(null=True, blank=True, choices=STATUS_CHOICES, default='CREATED')
    user_type = models.TextField(null=True, blank=True, choices=USER_TYPE_CHOICES, default=None)
    is_test = models.BooleanField(default=False, db_index=True)
    client_tier = models.TextField(choices=TIER_CHOICES, null=True, blank=True, default=STANDARD)

    objects = UserManager()


class BinanceAccount(models.Model):
    slug = models.CharField(max_length=32, unique=False,
                            default=make_slug, db_index=True)
    makerCommission = models.IntegerField()
    takerCommission = models.IntegerField()
    buyerCommission = models.IntegerField()
    sellerCommission = models.IntegerField()
    canTrade = models.BooleanField()
    canWithdraw = models.BooleanField()
    canDeposit = models.BooleanField()
    updateTime = models.BigIntegerField()
    accountType = models.CharField(max_length=60, null=False, blank=False)
    balances = ArrayField(models.JSONField(blank=True, null=True, default=dict),
                          default=list, blank=True)
    permissions = ArrayField(models.TextField(blank=True, null=True),
                             default=list, blank=True)
    url = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING,
                             related_name="binance_account_user",
                             blank=True, null=True, default=None)


class SymbolInfo(models.Model):
    slug = models.CharField(max_length=32, unique=False, default=make_slug, db_index=True)
    symbol = models.CharField(max_length=20, null=False, blank=False, unique=True, db_index=True)
    status = models.CharField(max_length=30, null=False, blank=False)
    baseAsset = models.CharField(max_length=10, null=False, blank=False)
    quoteAsset = models.CharField(max_length=10, null=False, blank=False)
    baseAssetPrecision = models.IntegerField()
    quotePrecision = models.IntegerField()
    quoteAssetPrecision = models.IntegerField()
    baseCommissionPrecision = models.IntegerField()
    quoteCommissionPrecision = models.IntegerField()
    orderTypes = ArrayField(models.TextField(blank=True, null=True), default=list, blank=True)
    icebergAllowed = models.BooleanField()
    ocoAllowed = models.BooleanField()
    quoteOrderQtyMarketAllowed = models.BooleanField()
    isSpotTradingAllowed = models.BooleanField()
    isMarginTradingAllowed = models.BooleanField()
    permissions = ArrayField(models.TextField(blank=True, null=True), default=list, blank=True)
    exchange_name = models.CharField(max_length=100, null=False, blank=False, default="Binance")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    filters = ArrayField(models.JSONField(blank=True, null=True, default=dict),
                         default=list, blank=True)

    def __str__(self):
        return self.symbol


class SingletonModel(models.Model):

    class Meta:
        abstract = True

    def set_cache(self):
        cache.set(self.__class__.__name__, self)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

        self.set_cache()

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                obj.set_cache()
        return cache.get(cls.__name__)


class GrabberSettings(SingletonModel):
    STATE_ACTIVE = 'ACTIVE'
    STATE_INACTIVE = 'INACTIVE'
    STATE_SUSPENDED = 'SUSPENDED'
    STATE_CHOICES = (
        (STATE_ACTIVE, 'ACTIVE'),
        (STATE_INACTIVE, 'INACTIVE'),
        (STATE_SUSPENDED, 'SUSPENDED'),
    )

    slug = models.CharField(max_length=32, unique=False, default=make_slug)
    is_running = models.BooleanField(default=False, null=False)
    symbols = ArrayField(models.TextField(blank=True, null=True), default=list, blank=True)
    account_keys = ArrayField(models.TextField(blank=True, null=True), default=list, blank=True)
    state = models.TextField(null=True, blank=True, choices=STATE_CHOICES, default=None)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="grabber_settings_user")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class GrabberSettingsRecords(models.Model):
    STATE_ACTIVE = 'ACTIVE'
    STATE_INACTIVE = 'INACTIVE'
    STATE_SUSPENDED = 'SUSPENDED'
    STATE_CHOICES = (
        (STATE_ACTIVE, 'ACTIVE'),
        (STATE_INACTIVE, 'INACTIVE'),
        (STATE_SUSPENDED, 'SUSPENDED'),
    )

    slug = models.CharField(max_length=32, unique=False, default=None)
    is_running = models.BooleanField(default=None, blank=True, null=True)
    symbols = ArrayField(models.TextField(blank=True, null=True), default=list, blank=True)
    account_keys = ArrayField(models.TextField(blank=True, null=True), default=list, blank=True)
    state = models.TextField(null=True, blank=True, choices=STATE_CHOICES, default=None)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="grabber_settings_record_user")
    created = models.DateTimeField()
    updated = models.DateTimeField()
    is_record_created = models.BooleanField(default=None, blank=True, null=True)
    slug_record = models.CharField(max_length=32, unique=False, default=make_slug)
    created_record = models.DateTimeField(auto_now_add=True)


@receiver(signals.post_save, sender=GrabberSettings)
def on_create_or_updated_grabber_settings_record(sender, instance, **kwargs):
    cloned_grabber_settings = {k: v for k, v in vars(instance).items() if k not in ('id', '_state')}
    cloned_grabber_settings['is_record_created'] = kwargs['created']
    GrabberSettingsRecords.objects.create(**dict(cloned_grabber_settings))


class SymbolEarliestTimestamp(models.Model):
    slug = models.CharField(max_length=32, unique=False, default=make_slug, db_index=True)
    symbol = models.CharField(max_length=20, null=False, blank=False, db_index=True)
    interval = models.CharField(max_length=2, null=False, blank=False, db_index=True)
    earliest_timestamp = models.BigIntegerField(blank=True, null=True, default=None)
    earliest_datetime = models.DateTimeField(blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="symbol_earliest_timestamp_user")


class BinanceAccountStatus(models.Model):
    slug = models.CharField(max_length=32, unique=False, default=make_slug, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="binance_account_status_user")
    status = models.TextField(null=True, blank=True, default=None)


class CoinInfo(models.Model):
    slug = models.CharField(max_length=32, unique=False, default=make_slug, db_index=True)
    coin = models.CharField(max_length=10, null=False, blank=False, unique=True, db_index=True)
    depositAllEnable= models.BooleanField()
    withdrawAllEnable = models.BooleanField()
    name = models.TextField(blank=True, null=True)
    free = models.FloatField()
    locked = models.FloatField()
    freeze = models.FloatField()
    withdrawing = models.FloatField()
    ipoing = models.FloatField()
    ipoable = models.FloatField()
    storage = models.FloatField()
    isLegalMoney = models.BooleanField()
    trading = models.BooleanField()
    networkList = ArrayField(models.JSONField(blank=True, null=True, default=dict),
                             default=list, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="coin_info_user")
