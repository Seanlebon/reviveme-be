from typing import Any

from flask import Response, request

from reviveme import db
from reviveme.models import Thread

from . import bp


@bp.route("/threads", methods=["GET"])
def thread_list():
    # TODO: figure out how to serialize our models properly
    threads = db.session.execute(db.select(Thread)).scalars().all()
    return [thread.serialize() for thread in threads]


@bp.route("/threads/<int:id>", methods=["GET"])
def thread_detail(id):
    thread = db.get_or_404(Thread, id)
    return thread.serialize()


@bp.route("/threads", methods=["POST"])
def thread_create():
    data: Any = request.json  # the :Any silences pylance errors
    # TODO validate incoming data
    # TODO: get author_id from token once auth is implemented
    thread = Thread(title=data["title"], content=data["content"], author_id=1)
    db.session.add(thread)
    db.session.commit()
    return Response(status=201)


@bp.route("/threads/<int:id>", methods=["PUT"])
def thread_update(id):
    thread = db.get_or_404(Thread, id)
    data: Any = request.json
    # TODO validate incoming data
    thread.title = data["title"]
    thread.content = data["content"]
    db.session.commit()
    return Response(status=200)


@bp.route("/threads/<int:id>", methods=["DELETE"])
def thread_delete(id):
    thread = db.get_or_404(Thread, id)
    db.session.delete(thread)
    db.session.commit()
    return Response(status=200)
