from flask import Response, request, jsonify
from marshmallow import Schema, fields, post_load, validate

from reviveme import db
from reviveme.models import Thread
from . import bp


class ThreadSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    content = fields.Str(required=True)
    
    author_id = None # set this before calling load()

    @post_load
    def make_thread(self, data, **kwargs) -> Thread:
        return Thread(**data, author_id=self.author_id)

@bp.route("/threads", methods=["GET"])
def thread_list():
    threads = db.session.execute(db.select(Thread).where(Thread.deleted == False)).scalars().all()
    return [thread.serialize() for thread in threads]


@bp.route("/threads/<int:id>", methods=["GET"])
def thread_detail(id):
    thread = db.get_or_404(Thread, id)
    return thread.serialize()


@bp.route("/threads", methods=["POST"])
def thread_create():
    schema = ThreadSchema()
    schema.author_id = 1 # TODO: get author_id from token once auth is implemented
    thread = schema.load(request.get_json())
    db.session.add(thread)
    db.session.commit()
    return Response(status=201)


@bp.route("/threads/<int:id>", methods=["PUT"])
def thread_update(id):
    thread = db.get_or_404(Thread, id)
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
