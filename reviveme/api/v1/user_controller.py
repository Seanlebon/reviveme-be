from reviveme import db
from reviveme.models import User

from . import bp


@bp.route("/users", methods=["GET"])
def users_list():
    # TODO: figure out how to serialize our models properly
    users = db.session.execute(db.select(User)).scalars().all()
    return [user.serialize() for user in users]
