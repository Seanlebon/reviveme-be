from flask import Response, request, jsonify
from marshmallow import Schema, fields, post_load, validate
from sqlalchemy import select, func

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

class UpVoteSchema(Schema): # TODO: move these schema into separate files
    upvote = fields.Boolean(required=True)
    user_id = fields.Int(required=True)
    
class DownVoteSchema(Schema):
    downvote = fields.Boolean(required=True)
    user_id = fields.Int(required=True)

def get_thread_score(thread_id):
    upvotes = db.session.execute(
        select(func.count("*")).select_from(ThreadVote).where(ThreadVote.thread_id == thread_id, ThreadVote.upvote == True)
    ).scalar()
    downvotes = db.session.execute(
        select(func.count("*")).select_from(ThreadVote).where(ThreadVote.thread_id == thread_id, ThreadVote.upvote == False)
    ).scalar()
    return upvotes - downvotes

@bp.route("/threads", methods=["GET"])
def thread_list():
    threads = db.session.execute(db.select(Thread).where(Thread.deleted == False)).scalars().all()
    return [thread.serialize() | {'score': get_thread_score(thread.id)} for thread in threads]


@bp.route("/threads/<int:id>", methods=["GET"])
def thread_detail(id):
    thread = db.get_or_404(Thread, id)
    resp_data = thread.serialize()
    resp_data['score'] = get_thread_score(id)
    return resp_data


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
