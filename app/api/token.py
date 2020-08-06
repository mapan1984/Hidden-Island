from flask import jsonify
from flask_login import current_user

from app.api import api
from app.api.decorators import login_required
from app.api.errors import unauthorized


@api.route('/tokens/', methods=['GET'])
@login_required
def get_token():
    """通过邮件与密码的认证方式获得token
    Request:
        GET /api/tokens/ http1.1
        Authorization: Basic ${user_email}:${User_password}

    curl --user username:password 'http://localhost:5000/api/tokens/'
    """
    if hasattr(current_user, '_token_used'):
        return unauthorized('must use username/password to apply token')
    return jsonify({
        'token': current_user.generate_auth_token(expiration=3600),
        'expiration': 3600
    })
