from functools import wraps

from flask import abort
from flask_login import current_user

from app.models import Permission


def permission_required(permission):
    def decorator(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return fun(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fun):
    return permission_required(Permission.ADMINISTER)(fun)


def author_required(fun):
    return permission_required(Permission.WRITE_ARTICLES)(fun)
