from typing import Any

from flask import Response, request

from reviveme import db
from reviveme.models import Thread

from . import bp


@bp.route("/users", methods=["GET"])
def users_list():
    # TODO: figure out how to serialize our models properly
    users = db.session.execute(db.select(User)).scalars().all()
    return [{"username": user.username, "email": user.email} for user in users]
