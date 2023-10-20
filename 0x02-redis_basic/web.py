#!/usr/bin/env python3
"""
The core of the function is very simple. It uses the requests
module to obtain the HTML content of a particular URL and returns it.
"""
import redis
import requests
from functools import wraps
from typing import Callable

redis_store = redis.Redis()


def data_cacher(method: Callable) -> Callable:
    """
    caches the output of fetched data.
    """
    @wraps(method)
    def invoker(url) -> str:
        """
        The wrapper function for caching the output.
        """
        redis_store.incr(f'count:{url}')
        result = redis_store.get(f'result:{url}')
        if result:
            return result.decode('utf-8')
        res = method(url)
        redis_store.set(f'count:{url}', 0)
        redis_store.setex(f'result:{url}', 10, res)
        return res
    return invoker


@data_cacher
def get_page(url: str) -> str:
    """
    returns the content of a URL after caching the request's response
    and tracking the request.
    """
    return requests.get(url).text
