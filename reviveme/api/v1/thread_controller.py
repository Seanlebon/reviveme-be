from flask import Response, request, jsonify
from marshmallow import Schema, fields, post_load, pre_dump, post_dump, validate
from sqlalchemy import select, func

import copy

from reviveme import db
from reviveme.models import Thread, ThreadVote
from . import bp


class ThreadSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    content = fields.Str(required=True)
    author_id = fields.Int(required=True) # TODO: get author_id from token once auth is implemented

    @post_load
    def make_thread(self, data, **kwargs) -> Thread:
        return Thread(**data)

class ThreadResponseSchema(Schema):
    id = fields.Int()
    author_username = fields.Function(lambda obj: obj.author.username if not obj.deleted else None)
    title = fields.Function(lambda obj: obj.title if not obj.deleted else None)
    content = fields.Function(lambda obj: obj.content if not obj.deleted else None)
    deleted = fields.Bool(required=True)

    upvoted = fields.Bool()
    downvoted = fields.Bool()
    score = fields.Int()

    def get_author_username(self, obj: Thread):
        return obj.author.username if not obj.deleted else None

    def get_title(self, obj: Thread):
        return obj.title if not obj.deleted else None
    
    def get_content(self, obj: Thread):
        return obj.content if not obj.deleted else None

    @post_dump(pass_original=True)
    def append_vote_data(self, data, thread: Thread, **kwargs):
        upvoted, downvoted = get_thread_upvoted(
            thread.id, user_id=self.context['user_id']
        )
        return {
            **data,
            'upvoted': upvoted,
            'downvoted': downvoted,
            'score': get_thread_score(thread_id=thread.id)
        }


def get_thread_score(thread_id):
    upvotes = db.session.execute(
        select(func.count("*")).select_from(ThreadVote).where(ThreadVote.thread_id == thread_id, ThreadVote.upvote == True)
    ).scalar()
    downvotes = db.session.execute(
        select(func.count("*")).select_from(ThreadVote).where(ThreadVote.thread_id == thread_id, ThreadVote.upvote == False)
    ).scalar()
    return upvotes - downvotes

def get_thread_upvoted(thread_id, user_id):
    upvote_db_val: bool = db.session.execute(
        select(ThreadVote.upvote).where(ThreadVote.thread_id == thread_id, ThreadVote.user_id == user_id)
    ).scalar()

    if upvote_db_val is None:
        return False, False
    return upvote_db_val, not upvote_db_val

@bp.route("/threads", methods=["GET"])
def thread_list():
    threads = db.session.execute(db.select(Thread).where(Thread.deleted == False)).scalars().all()

    schema = ThreadResponseSchema(context={'user_id': 1})
    return [schema.dump(thread) for thread in threads]


@bp.route("/threads/<int:id>", methods=["GET"])
def thread_detail(id):
    thread = db.get_or_404(Thread, id)
    return ThreadResponseSchema(context={'user_id': 1}).dump(thread)


@bp.route("/threads", methods=["POST"])
def thread_create():
    schema = ThreadSchema()
    thread = schema.load(request.get_json())
    db.session.add(thread)
    db.session.commit()
    return Response(status=201)


@bp.route("/threads/<int:id>", methods=["PUT"])
def thread_update(id):
    thread = db.get_or_404(Thread, id)
    if thread.deleted:
        return Response(status=400, response=f"Thread with id {id} has been deleted")

    data = request.get_json()

    errors = ThreadSchema().validate(data, partial=True)
    if errors:
        return jsonify(errors), 400

    thread.title = data.get("title", thread.title)
    thread.content = data.get("content", thread.content)
    db.session.commit()
    return Response(status=200)


@bp.route("/threads/<int:id>", methods=["DELETE"])
def thread_delete(id):
    thread = db.get_or_404(Thread, id)
    thread.deleted = True
    db.session.commit()
    return Response(status=200)
