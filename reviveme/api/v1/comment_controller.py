from __future__ import annotations

from typing import Any, List
from flask import Response, request

from reviveme import db
from reviveme.models import Comment, Thread

from . import bp

class CommentNode:
    '''
    Used to construct a tree of comments for easier serialization
    '''
    def __init__(self, comment: Comment):
        self.comment = comment
        self.children: List[CommentNode] = []

    def add_child(self, node: CommentNode):
        self.children.append(node)

    def serialize(self):
        return {
            **self.comment.serialize(),
            "children": [child.serialize() for child in self.children]
        }


@bp.route("/threads/<int:thread_id>/comments", methods=["GET"])
def comment_list(thread_id):
    db.get_or_404(Thread, thread_id) # 404 if thread doesn't exist

    comments = (
        db.session.execute(db.select(Comment).where(Comment.thread_id == thread_id).where(Comment.depth == 1))
        .scalars()
        .all()
    )
    depth = 2 # start at depth 2 since we already got depth 1
    top_level_comments = [CommentNode(comment) for comment in comments]
    # Save pointers to leaf nodes for easier insertion
    prev_level_comments = {node.comment.id: node for node in top_level_comments}
    while len(comments) > 0:
        new_nodes = {}

        comments = (
            db.session.execute(db.select(Comment).where(Comment.thread_id == thread_id).where(Comment.depth == depth))
            .scalars()
            .all()
        )
        for comment in comments:
            node = CommentNode(comment)
            parent = prev_level_comments[comment.parent_id]
            parent.add_child(node)
            new_nodes[comment.id] = node
        
        prev_level_comments = new_nodes
        depth += 1

    return [comment.serialize() for comment in top_level_comments]


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
    if "parent_id" in data:
        db.get_or_404(Comment, data["parent_id"])
        comment = Comment(
            content=data["content"],
            thread_id=thread_id,
            author_id=1,
            parent_id=data["parent_id"],
        )
    else:
        comment = Comment(
            content=data["content"], 
            thread_id=thread_id, 
            author_id=1
        )
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
    comment.deleted = True
    db.session.commit()
    return Response(status=200)
