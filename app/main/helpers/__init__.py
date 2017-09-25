import base64
import hashlib
import flask_login

from datetime import datetime
from functools import wraps
from flask import current_app, flash


def login_required(func):
    @wraps(func)
    @flask_login.login_required
    def decorated_view(*args, **kwargs):
        if flask_login.current_user.is_authenticated() and flask_login.current_user.role != 'supplier':
            flash('supplier-role-required', 'error')
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view
