from flask import jsonify

from app.exceptions import ValidationError

from app.api import api


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


def server_error(message):
    response = jsonify({'error': 'server error', 'message': message})
    response.status_code = 500
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    """ValidationError的全局异常处理函数"""
    return bad_request(e.args[0])


@api.errorhandler(404)
def page_not_found(error):
    return bad_request('page not found')


@api.errorhandler(403)
def page_forbindden(error):
    return forbidden('forbindden')


@api.errorhandler(500)
def internal_server_error(error):
    return server_error('internal server error')
