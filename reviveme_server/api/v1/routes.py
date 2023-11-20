from flask import request
from . import bp
from reviveme_server import db
from reviveme_server.models.models import *

@bp.route("/")
@bp.route("/index")
def index():
    return "Hello, World!"

@bp.route("/threads", methods=["GET"])
def thread_list():
    threads = db.session.execute(db.select(Thread)).scalars().all()
    return [ thread.serialize for thread in threads]

@bp.route("/threads/<id>", methods=["GET"])
def thread_get(id):
    thread = db.session.execute(db.select(Thread)).scalar()
    return thread.serialize

@bp.route("/threads", methods=["PUT"])
def create_thread():
    data = request.get_json()

    thread = Thread(
        title=data.get('title'),
        content=data.get('content'),
        author_id=data.get('author_id')
    )

    db.session.add(thread)
    db.session.commit()

    # TODO return 201: created
