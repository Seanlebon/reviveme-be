from flask import Blueprint

bp = Blueprint('v1', __name__)

from . import routes