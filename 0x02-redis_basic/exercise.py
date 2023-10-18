#!/usr/bin/env python3
"""

"""
import redis
import uuid
from typing import Union, Callable, Any
from functools import wraps



def count_calls(method: Callable) -> Callable:
    """
    count how many times methods of the Cache class are called.
    """
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        """
        Invoke the given method after incrementing its call counter
        """
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return invoker


def call_history(method: Callable) -> Callable:
    """
    store the history of inputs and outputs for a particular function.
    """
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        """
        returns the method's output after storing its inputs and outputs.
        """
        in_key = '{}:inputs'.format(method.__qualname__)
        out_key = '{}:outputs'.format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(in_key, str(args))
        output = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(out_key, output)
        return output
    return invoker


def replay(fn: Callable) -> None:
    """
    a replay function to display the history of calls of a particular function.
    """
    if fn is None or not hasattr(fn, '__self__'):
        return
    redis_store = getattr(fn.__self__, '_redis_', None)
    if not isinstance(redis_store, redis.Redis):
        return
    fxn_name = fn.__qualname__
    in_key = '{}:inputs'.format(fxn_name)
    out_key = '{}:outputs'.format(fxn_name)
    fxn_call_count = 0
    if redis_store.exists(fxn_name) != 0:
        fxn_call_count = int(redis_store.get(fxn_name))
    print('{} was called {} times:'.format(fxn_name, fxn_call_count))
    fxn_inputs = redis_store.lrange(in_key, 0, -1)
    fxn_outputs = redis_store.lrange(out_key, 0, -1)
    for fxn_input, fxn_output in zip(fxn_inputs, fxn_outputs):
        print('{}(*{}) -> {}'.format(
            fxn_name, fxn_input.decode('utf-8'), fxn_output,
            ))


class Cache:
    """
    A cache class
    """
    def __init__(self) -> None:
        """
        store an instance of the Redis client as a private variable
        named _redis (using redis.Redis())
        and flush the instance using flushdb.
        """
        self._redis = redis.Redis()
        self._redis.flushdb(True)


    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        store method that takes a data argument and returns a string
        The method should generate a random key (e.g. using uuid)
        store the input data in Redis using the random key & return the key.
        """
        data_key = str(uuid.uuid4())
        self._redis.set(data_key, data)
        return data_key


    def get(self, key: str,
            fn: Callable = None) -> Union[str, bytes, int, float]:
        """
        conserve the original Redis.get behavior if the key does not exist.
        """
        data = self._redis.get(key)
        return fn(data) if fn is not None else data


    def get_str(self, key: str) -> str:
        """
        automatically parametrize Cache.get of str
        """
        return self.get(key, lambda x: x.decode('utf-8'))


    def get_int(self, key: str) -> int:
        """
        automatically parametrize Cache.get of int.
        """
        return self.get(key, lambda x: int(x))
