"""
使用Authorization头部进行用户认证，有3种方式进行请求
1. 匿名用户：请求无Authorization头部或为`Authorization: Basic ${}:${}`，即username字段为空
2. 使用邮件与密码验证：请求为`Authorization: Basic ${user_email}:${User_password}`
3. 使用token进行验证：请求为`Authorization: Basic ${token}:${}`，即username字段代表token，密码字段为空
认证信息需使用base64进行编码
"""
from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth

from app.models import User, AnonymousUser

from app.api import api
from app.api.errors import unauthorized, forbidden


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password_or_token(email_or_token, password):
    """用户验证的回调函数，保存用户到g.current_user
    Returns:
        匿名用户或token/password验证成功返回True
        token/hassword验证失败返回False
    """
    if email_or_token == '':  # 匿名用户
        g.current_user = AnonymousUser()
        return True
    if password == '':  # 使用token验证
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    # 使用email和password验证
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    if user.verify_password(password):
        g.current_user = user
        return True
    else:
        return False


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    """拒绝已通过认证但没有确认账户的用户"""
    if not g.current_user.is_anonymous \
            and not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@api.route('/tokens/', methods=['GET'])
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({
        'token': g.current_user.generate_auth_token(expiration=3600),
        'expiration': 3600
    })
