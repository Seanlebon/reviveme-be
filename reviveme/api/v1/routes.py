from reviveme import db
from reviveme.models import Thread, User

from . import bp


@bp.route("/")
@bp.route("/index")
def index():
    return "Hello, World!"


@bp.route("/threads", methods=["GET"])
def thread_list():
    # TODO: figure out how to serialize our models properly
    threads = db.session.execute(db.select(Thread)).scalars().all()
    return [{"title": thread.title, "content": thread.content} for thread in threads]


@bp.route("/users", methods=["GET"])
def users_list():
    # TODO: figure out how to serialize our models properly
    users = db.session.execute(db.select(User)).scalars().all()
    return [{"username": user.username, "email": user.email} for user in users]
