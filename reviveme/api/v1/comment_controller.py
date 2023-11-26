from typing import Any

from flask import Response, request

from reviveme import db
from reviveme.models import Comment, Thread

from . import bp


@bp.route("/threads/<int:thread_id>/comments", methods=["GET"])
def comment_list(thread_id):
    comments = (
        db.session.execute(db.select(Comment).where(Comment.thread_id == thread_id))
        .scalars()
        .all()
    )
    return [comment.serialize() for comment in comments]


@bp.route("/comments/<int:comment_id>", methods=["GET"])
def comment_detail(comment_id):
    comment = db.get_or_404(Comment, comment_id)
    return comment.serialize()


@bp.route("/threads/<int:thread_id>/comments", methods=["POST"])
def comment_create(thread_id):
    data: Any = request.json
    if db.session.get(Thread, thread_id) is None:
        return Response(f"Thread with id {thread_id} not found", status=404)

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
