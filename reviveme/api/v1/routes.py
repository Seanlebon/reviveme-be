from typing import Any

from flask import Response, request

from reviveme import db
from reviveme.models import Comment, Thread, User

from . import bp


@bp.route("/")
@bp.route("/index")
def index():
    return "Hello, World!"
