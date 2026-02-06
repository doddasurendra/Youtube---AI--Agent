from __future__ import annotations

import functools
import time
from typing import Callable, TypeVar

F = TypeVar("F", bound=Callable[..., object])


def with_retry(attempts: int = 3, wait_seconds: float = 1.0, backoff: float = 2.0) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = wait_seconds
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt >= attempts:
                        raise
                    time.sleep(delay)
                    delay *= backoff
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
