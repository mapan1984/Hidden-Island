from flask import Blueprint

api = Blueprint('api', __name__)

from app.api import authentication, article, users, comments, errors
