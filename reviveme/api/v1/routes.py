from flask import request
from flask import Response

from reviveme import db
from reviveme.models import Thread, User, Comment

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
    return [{"id": thread.id, "author_id": thread.author_id, "title": thread.title, "content": thread.content} for thread in threads]

@bp.route("/threads/<int:id>", methods=["GET"])
def thread_detail(id):
    thread = db.get_or_404(Thread, id)
    return {"id": thread.id, "author_id": thread.author_id, "title": thread.title, "content": thread.content}

@bp.route("/threads", methods=["POST"])
def thread_create():
    data: Any = request.json # the :Any silences pylance errors
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

@bp.route("/threads/<int:thread_id>/comments", methods=["GET"])
def comment_list(thread_id):
    comments = db.session.execute(db.select(Comment).where(Comment.thread_id == thread_id)).scalars().all()
    return [{"id": comment.id, "content": comment.content} for comment in comments]

@bp.route("/comments/<int:comment_id>", methods=["GET"])
def comment_detail(comment_id):
    comment = db.get_or_404(Comment, comment_id)
    return {"id": comment.id, "content": comment.content}

@bp.route("/threads/<int:thread_id>/comments", methods=["POST"])
def comment_create(thread_id):
    data: Any = request.json
    if db.session.get(Thread, thread_id) is None:
        return Response(f'Thread with id {thread_id} not found', status=404)
    
    # TODO validate data in request body
    # TODO: get author_id from token once auth is implemented
    comment = Comment(content=data["content"], thread_id=thread_id, author_id=1)
    db.session.add(comment)
    db.session.commit()
    return Response(status=201)

@bp.route("/comments/<int:comment_id>", methods=["PUT"])
def comment_update(comment_id):
    comment = db.get_or_404(Comment, comment_id)
    data: Any = request.json
    # TODO validate incoming data
    comment.content = data["content"]
    db.session.commit()
    return Response(status=200)

@bp.route("/comments/<int:comment_id>", methods=["DELETE"])
def comment_delete(comment_id):
    comment = db.get_or_404(Comment, comment_id)
    db.session.delete(comment)
    db.session.commit()
    return Response(status=200)


@bp.route("/users", methods=["GET"])
def users_list():
    # TODO: figure out how to serialize our models properly
    users = db.session.execute(db.select(User)).scalars().all()
    return [{"username": user.username, "email": user.email} for user in users]
