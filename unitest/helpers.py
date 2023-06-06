import functools


def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                # new_args = args + (c if isinstance(c, tuple) else (c,))
                new_args = args + (c if isinstance(c, tuple) else (c,))
                f(*new_args)
        return wrapper
    return decorator


import logging
import coloredlogs


# # Here the logs are turned on
# logging.basicConfig(level=logging.FATAL,
#                     format='%(asctime)s - %(name)s - %(levelname)s'
#                     ' %(message)s')
#
# coloredlogs.install(level=logging.FATAL,
#                     format='%(asctime)s - %(name)s - %(levelname)s'
#                     ' %(message)s')
