"""
lazy.py: Lazy evaluation tools

Bottle Utils
2014 Outernet Inc <hello@outernet.is>
All rights reserved

Licensed under BSD license. See ``LICENSE`` file in the source directory.
"""

from functools import wraps


__all__ = ('Lazy', 'CachingLazy', 'lazy', 'caching_lazy')


class Lazy(object):
    """ Proxy object that evaluates a function when its value is needed

    The basic idea is pretty much stolen from Django's
    ``utils.functional.lazy``.
    """

    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def _eval(self):
        return self._func(*self._args, **self._kwargs)

    @staticmethod
    def _eval_other(other):
        try:
            return other._eval()
        except AttributeError:
            return other

    def __getattr__(self, attr):
        obj = self._eval()
        return getattr(obj, attr)

    # We don't need __setattr__ and __delattr__ because the proxy object is not
    # really an object.

    def __getitem__(self, key):
        obj = self._eval()
        return obj.__getitem__(key)

    @property
    def __class__(self):
        return self._eval().__class__

    def __repr__(self):
        return '<Lazy {}>'.format(self._func)

    def __str__(self):
        return str(self._eval())

    def __bytes__(self):
        return bytes(self._eval())

    def __call__(self):
        return self._eval()()

    def __format__(self, format_spec):
        return self._eval().__format__(format_spec)

    # Being explicit about all comparison methods to avoid double-calls

    def __lt__(self, other):
        other = self._eval_other(other)
        return self._eval() < other

    def __le__(self, other):
        other = self._eval_other(other)
        return self._eval() <= other

    def __gt__(self, other):
        other = self._eval_other(other)
        return self._eval() > other

    def __ge__(self, other):
        other = self._eval_other(other)
        return self._eval() >= other

    def __eq__(self, other):
        other = self._eval_other(other)
        return self._eval() == other

    def __ne__(self, other):
        other = self._eval_other(other)
        return self._eval() != other

    # We mostly use this for strings, so having just __add__ is fine

    def __add__(self, other):
        other = self._eval_other(other)
        return self._eval() + other

    def __radd__(self, other):
        return self._eval_other(other) + self._eval()

    def __bool__(self):
        return bool(self._eval())

    def __hash__(self):
        return hash(self._eval())


class CachingLazy(Lazy):
    """ Caching version of the Lazy class """

    def __init__(self, *args, **kwargs):
        self._called = False
        self._cached = None
        super(CachingLazy, self).__init__(*args, **kwargs)

    def _eval(self):
        if self._called:
            return self._cached
        self._called = True
        self._cached = self._func(*self._args, **self._kwargs)
        return self._cached


def lazy(fn):
    """ Converts a function into lazily evaluated version """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return Lazy(fn, *args, **kwargs)
    return wrapper


def caching_lazy(fn):
    """ Convert a function into lazily evaluated version which caches value """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return CachingLazy(fn, *args, **kwargs)
    return wrapper
