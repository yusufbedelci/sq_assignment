from functools import wraps
from exceptions import RateLimitException
import time


def rate_limit(max_calls: int, period: int):
    def decorator(func):
        last_call_time = [0]
        calls_in_period = [0]

        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            # Reset count if period has passed
            if current_time - last_call_time[0] > period:
                calls_in_period[0] = 0
                last_call_time[0] = current_time

            if calls_in_period[0] < max_calls:
                calls_in_period[0] += 1
                return func(*args, **kwargs)
            else:
                raise RateLimitException(f"Rate limit exceeded. Try again after one minute.")

        return wrapper

    return decorator
