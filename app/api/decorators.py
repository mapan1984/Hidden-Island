from functools import wraps

from flask import request
from flask_login import current_user

from app.api.errors import forbidden, unauthorized


EXEMPT_METHODS = set(['OPTIONS'])


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                return forbidden('Insufficient permissions')
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            return (
                unauthorized('Invalid credentials'),
                401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'}
            )
        return func(*args, **kwargs)
    return decorated_view

