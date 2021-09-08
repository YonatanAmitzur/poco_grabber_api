""" PoCo specific Api & Models validators """
import re
from django.core import validators
from django.core.exceptions import ValidationError


def url(value, blank=None):  # pylint: disable=unused-argument
    """ return None if value is a valid url address string, raise exception otherwise"""
    def validate_value(single_value):
        if not rgx_url.match(single_value):
            raise ValidationError('Not a valid URL', 'ERR_URL0')

    if blank is True:
        if value == '':
            return
        elif value is None:
            return
    elif isinstance(value, dict):
        for var in value.values():
            validate_value(var)
    else:
        validate_value(value)


def phone(value, blank=True):  # pylint: disable=unused-argument
    """ return None if value is a valid phone numberstring, raise exception otherwise"""
    def validate_value(single_value):
        if rgx_phone_invalid_chars.findall('%s' % single_value):
            raise ValidationError('Invalid chars in phone number', 'ERR_PHONE0')
        stripped = re.sub(rgx_phone_strip_chars, '', '%s' % single_value)
        min(7)(stripped, blank)
        max(10)(stripped, blank)

    if blank and value in ('', None):
        return
    elif isinstance(value, dict):
        for var in value.values():
            validate_value(var)
    else:
        validate_value(value)


def lower_case(value, blank=None):  # pylint: disable=unused-argument, invalid-name
    """regex search to force no capital letters in email addresses"""
    if re.search(r'[A-Z]', value):
        raise ValidationError(
            'the email must not contain any upper case letters',
            'ERR_EMAIL_HAS_UPPER')


def email(value, blank=None):  # pylint: disable=unused-argument
    """ return None if value is a valid email address string, raise exception otherwise"""
    def validate_value(single_value):
        if not isinstance(single_value, str):
            return
        try:
            validators.validate_email(single_value.strip())
        except ValidationError as ex:
            raise ValidationError('%s' % ex, 'ERR_EMAIL0')

    if blank and value in ('', None):
        return
    elif isinstance(value, dict):
        for var in value.values():
            validate_value(var)
    else:
        validate_value(value)


# precompiled utility Regexes
rgx_javascript_xss = re.compile(r'javascript\:', re.IGNORECASE)
rgx_url = re.compile(
    r'^((http|https|ftp):\/\/)?((.*?):(.*?)@)?' +
    r'([a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])' +
    r'((\.[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])*(\.[a-zA-Z0-9]+)+)' +
    r'(:([0-9]{1,5}))?((\/.*?)(\?(.*?))?(\#(.*))?)?$', re.IGNORECASE)

unicode_ctrl_chars = '\u200e\u200f'
rgx_phone_invalid_chars = re.compile(
    r'([^0-9()\.\-#x\+ %s]+)' % unicode_ctrl_chars, re.IGNORECASE)
rgx_phone_strip_chars = re.compile(
    r'([()\-\.#x+ %s]+)' % unicode_ctrl_chars, re.IGNORECASE)

rgx_bank_name = re.compile(r'(?!^\d+$)^.+$')

