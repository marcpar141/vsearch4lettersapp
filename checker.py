from flask import session
from functools import wraps


def check_loggen_in(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'logged_in' in session:
            return func(*args, **kwargs)
        return 'NIE jesteś zalogowany'

    return wrapper
