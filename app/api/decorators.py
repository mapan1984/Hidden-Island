from functools import wraps

from flask import g
from flask_login import current_user

from app.api.errors import forbidden


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.current_user:
                if not g.current_user.can(permission):
                    return forbidden('Insufficient permissions')
            else:
                if not current_user.can(permission):
                    return forbidden('Insufficient permissions')
            return f(*args, **kwargs)
        return decorated_function
    return decorator
