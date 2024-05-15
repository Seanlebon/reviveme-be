from __future__ import annotations

from typing import Any, List
from flask import Response, jsonify, request

from reviveme import db
from reviveme.models import CommentVote
from reviveme.models.thread import Thread
from reviveme.models.comment import Comment

from marshmallow import Schema, fields, post_load, post_dump, validate, validates, ValidationError
from sqlalchemy import select

from . import bp

class CommentRequestSchema(Schema):
    content = fields.Str(required=True, validate=validate.Length(min=1))
    parent_id = fields.Int()
    author_id = fields.Int(required=True) # TODO: get author_id from token once auth is implemented
    
    thread_id = None # set this before calling load()

    @validates("parent_id")
    def validate_parent_id(self, parent_id):
        if parent_id is not None and db.session.get(Comment, parent_id) is None:
            raise ValidationError(f"Comment with id {parent_id} does not exist")

    @post_load
    def make_comment(self, data, **kwargs) -> Comment:
        return Comment(**data, thread_id=self.context['thread_id'])

class CommentResponseSchema(Schema):
    id = fields.Int()
    author_username = fields.Function(lambda obj: obj.author.username if not obj.deleted else None)
    thread_id = fields.Int()
    content = fields.Function(lambda obj: obj.content if not obj.deleted else None)
    deleted = fields.Bool()
    created_at = fields.DateTime()
    score = fields.Int()

    @post_dump(pass_original=True)
    def append_vote_data(self, data, comment: Comment, **kwargs):
        upvoted, downvoted = get_comment_upvoted(comment.id, user_id=self.context['user_id'])
        return {
            **data,
            'upvoted': upvoted,
            'downvoted': downvoted,
        }

class CommentNode:
    '''
    Used to construct a tree of comments for easier serialization
    '''
    def __init__(self, comment: Comment):
        self.comment = comment
        self.children: List[CommentNode] = []

    def add_child(self, node: CommentNode):
        self.children.append(node)

    def serialize(self, schema: CommentResponseSchema):
        return {
            **schema.dump(self.comment),
            'children': [child.serialize(schema) for child in self.children]
        }

def get_comment_upvoted(comment_id, user_id):
    upvote_db_val: bool = db.session.execute(
        select(CommentVote.upvote).where(CommentVote.comment_id == comment_id, CommentVote.user_id == user_id)
    ).scalar()

    if upvote_db_val is None:
        return False, False
    return upvote_db_val, not upvote_db_val

@bp.route("/threads/<int:thread_id>/comments", methods=["GET"])
def comment_list(thread_id):
    db.get_or_404(Thread, thread_id) # 404 if thread doesn't exist

    sort_by = request.args.get("sortby", "newest", type=str)

    select_statement = db.select(Comment).where(Comment.thread_id == thread_id).where(Comment.depth == 1)
    if sort_by == "newest":
        select_statement = select_statement.order_by(Comment.created_at.desc())
    elif sort_by == "top":
        select_statement = select_statement.order_by(Comment.score.desc())

    comments = db.session.execute(select_statement).scalars().all()
    
    depth = 2 # start at depth 2 since we already got depth 1
    top_level_comments = [CommentNode(comment) for comment in comments]
    # Save pointers to leaf nodes for easier insertion
    prev_level_comments = {node.comment.id: node for node in top_level_comments}
    while len(comments) > 0:
        new_nodes = {}

        select_statement = db.select(Comment).where(Comment.thread_id == thread_id).where(Comment.depth == depth)
        if sort_by == "newest":
            select_statement = select_statement.order_by(Comment.created_at.desc())
        elif sort_by == "top":
            select_statement = select_statement.order_by(Comment.score.desc())
        
        comments = db.session.execute(select_statement).scalars().all()
        
        for comment in comments:
            node = CommentNode(comment)
            parent = prev_level_comments[comment.parent_id]
            parent.add_child(node)
            new_nodes[comment.id] = node
        
        prev_level_comments = new_nodes
        depth += 1

    schema = CommentResponseSchema(context={'user_id': 1})
    return [node.serialize(schema) for node in top_level_comments]


@bp.route("/comments/<int:comment_id>", methods=["GET"])
def comment_detail(comment_id):
    comment = db.get_or_404(Comment, comment_id)
    return CommentResponseSchema(context={'user_id': 1}).dump(comment)


@bp.route("/threads/<int:thread_id>/comments", methods=["POST"])
def comment_create(thread_id):
    data: Any = request.json
    if db.session.get(Thread, thread_id) is None:
        return Response(f"Thread with id {thread_id} not found", status=404)

    schema = CommentRequestSchema(context={'thread_id': thread_id})
    comment = schema.load(data)
    db.session.add(comment)
    db.session.commit()
    return Response(status=201)


@bp.route("/comments/<int:comment_id>", methods=["PUT"])
def comment_update(comment_id):
    comment = db.get_or_404(Comment, comment_id)
    if comment.deleted:
        return Response(status=400, response=f"Comment with id {comment_id} has been deleted")

    data: Any = request.json

    errors = CommentRequestSchema().validate(data, partial=("content",))
    if errors:
        return jsonify(errors), 400

    comment.content = data["content"]
    db.session.commit()
    return Response(status=200)


@bp.route("/comments/<int:comment_id>", methods=["DELETE"])
def comment_delete(comment_id):
    comment = db.get_or_404(Comment, comment_id)
    comment.deleted = True
    db.session.commit()
    return Response(status=200)
