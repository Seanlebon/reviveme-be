from flask import Blueprint

bp = Blueprint("v1", __name__)

from . import comment_controller, routes, thread_controller, user_controller
