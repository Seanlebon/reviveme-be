from flask import request
from flask import Response

from reviveme import db
from reviveme.models import Thread, User

from typing import Any

from . import bp


@bp.route("/")
@bp.route("/index")
def index():
    return "Hello, World!"


@bp.route("/threads", methods=["GET"])
def thread_list():
    # TODO: figure out how to serialize our models properly
    threads = db.session.execute(db.select(Thread)).scalars().all()
    return [{"id": thread.id, "title": thread.title, "content": thread.content} for thread in threads]

@bp.route("/threads/<int:id>", methods=["GET"])
def thread_detail(id):
    thread = db.get_or_404(Thread, id)
    return {"id": thread.id, "title": thread.title, "content": thread.content}

@bp.route("/threads", methods=["POST"])
def thread_create():
    data: Any = request.json # the :Any silences pylance errors
    # TODO validate incoming data
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

@bp.route("/users", methods=["GET"])
def users_list():
    # TODO: figure out how to serialize our models properly
    users = db.session.execute(db.select(User)).scalars().all()
    return [{"username": user.username, "email": user.email} for user in users]
