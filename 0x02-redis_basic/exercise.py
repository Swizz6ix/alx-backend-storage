#!/usr/bin/env python3
"""
writing to redis database using python in place of redis shell.
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
    def invoker(self, *args, **kwargs):
        """
        Invoke the given method after incrementing its call counter
        """
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return invoker


def call_history(method: Callable) -> Callable:
    """
    store the history of inputs and outputs for a particular function.
    """
    key = method.__qualname__
    inputs = key + ":inputs"
    outputs = key + ":outputs"
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        """
        returns the method's output after storing its inputs and outputs.
        """
        self._redis.rpush(inputs, str(args))
        data = method(self, *args, **kwargs)
        self._redis.rpush(outputs, str(data))
        return data
    return invoker


def replay(fn: Callable) -> None:
    """
    a replay function to display the history of calls of a particular function.
    """
    fxn_name = fn.__qualname__
    cache = redis.Redis()
    calls = cache.get(fxn_name).decode('utf-8')
    print('{} was called {} times:'.format(fxn_name, calls))
    fxn_inputs = cache.lrange(fxn_name + ":inputs", 0, -1)
    fxn_outputs = cache.lrange(fxn_name + ":outputs", 0, -1)
    for fxn_input, fxn_output in zip(fxn_inputs, fxn_outputs):
        print("{}(*{}) -> {}".format(
            fxn_name, fxn_input.decode('utf-8'), fxn_output.decode('utf-8')
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

    @count_calls
    @call_history
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
