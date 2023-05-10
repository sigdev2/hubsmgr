# origin: https://stackoverflow.com/questions/33672412/python-functools-lru-cache-with-class-methods-release-object
import functools
import weakref

def weak_lru(maxsize=128, typed=False):
    r'LRU Cache decorator that keeps a weak reference to "self"'
    def wrapper(func):

        @functools.lru_cache(maxsize, typed)
        def _func(_self, *args, **kwargs):
            return func(_self(), *args, **kwargs)

        func.cache_clear = _func.cache_clear

        @functools.wraps(func)
        def inner(self, *args, **kwargs):
            return _func(weakref.ref(self), *args, **kwargs)

        return inner

    return wrapper
