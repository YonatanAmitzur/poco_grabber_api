from functools import lru_cache
from django.contrib.auth import get_user_model as django_get_user_model
from collections import defaultdict

# pylint: disable=too-many-lines, unused-variable
memoize_functions = defaultdict(list)

@lru_cache()
def get_user_model():
    return django_get_user_model()


def memoize(*args, **kwargs):
    """ simple wrapper for lru_cache so we can clear it with utility functions """

    def decorator(func):
        group = kwargs.pop('group', 'default')
        func = lru_cache(*args, **kwargs)(func)
        memoize_functions[group].append(func)
        return func

    return decorator


def clear_memoize_functions(group='default', **kwargs):
    """ clear function for memoize
        NOTE: sub_groups is future stub; not currently implemented
    """
    kwargs.pop('sub_groups', None)
    for func in memoize_functions[group]:
        func.cache_clear()


def clear_all_memoize_functions():
    """ clear function for memoize """
    for group in memoize_functions.keys():
        clear_memoize_functions(group)


@lru_cache()
def get_system_user():
    """Return System user (pk=1)"""
    return get_user_model().objects.get(id=1)