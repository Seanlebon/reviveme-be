from . import bp
from reviveme_server import db
from reviveme_server.models.models import *


@bp.route("/")
@bp.route("/index")
def index():
    return "Hello, World!"

@bp.route("/threads", methods=["GET"])
def thread_list():
    # TODO: figure out how to serialize our models properly
    threads = db.session.execute(db.select(Thread)).scalars().all()
    return [ {'title': thread.title, 'content': thread.content} for thread in threads]
