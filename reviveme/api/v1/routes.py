from reviveme import db
from reviveme.models import Thread

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
