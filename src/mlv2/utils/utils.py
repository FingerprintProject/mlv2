import time
from functools import wraps


def timeit(func):
    @wraps(func)
    def timeit_wrapper(self, *args, **kwargs):
        start_time = time.perf_counter()
        result = func(self, *args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time

        self.logger.info(f"Function {func.__name__} Took {total_time:.4f} seconds")
        return result

    return timeit_wrapper
