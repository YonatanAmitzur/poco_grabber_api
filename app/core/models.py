import uuid
from django.db import models
from django.db.models import PositiveIntegerField
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from core.utils import validators


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
    is_test = models.BooleanField(default=False, db_index=True)
    client_tier = models.TextField(choices=TIER_CHOICES, null=True, blank=True, default=STANDARD)

    objects = UserManager()

