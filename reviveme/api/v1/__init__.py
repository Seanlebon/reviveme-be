from flask import Blueprint, jsonify
import marshmallow as ma

bp = Blueprint("v1", __name__)

@bp.errorhandler(ma.ValidationError)
def handle_validation_error(error):
    return jsonify(error.messages), 400

from . import comment_controller, routes, thread_controller, user_controller
