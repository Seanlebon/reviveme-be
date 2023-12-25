from . import bp
from flask import Response, request
from marshmallow import Schema, fields

from reviveme import db
from reviveme.models import ThreadVote, CommentVote, Thread, Comment

from sqlalchemy import select

class UpVoteSchema(Schema): # TODO: move these schema into separate files
    upvote = fields.Boolean(required=True)
    user_id = fields.Int(required=True)
    
class DownVoteSchema(Schema):
    downvote = fields.Boolean(required=True)
    user_id = fields.Int(required=True)

def handle_upvote(VoteClass, item_id):
    data = UpVoteSchema().load(request.get_json())

    vote = db.session.execute(
        select(VoteClass).where(VoteClass.item_id == item_id, VoteClass.user_id == data['user_id'])
    ).scalars().first()

    if vote is None and data['upvote']: # if no vote and user wants to upvote
        vote = VoteClass(user_id=data['user_id'], item_id=item_id, upvote=True)
        db.session.add(vote)
    elif vote.upvote and not data['upvote']: # if user upvoted and now wants to remove upvote
        db.session.delete(vote)
    elif not vote.upvote and data['upvote']: # if user downvoted and now wants to upvote
        vote.upvote = True
        db.session.add(vote)
    
    db.session.commit()

def handle_downvote(VoteClass, item_id):
    data = DownVoteSchema().load(request.get_json())

    vote = db.session.execute(
        select(VoteClass).where(VoteClass.item_id == item_id, ThreadVote.user_id == data['user_id'])
    ).scalars().first()

    if vote is None and data['downvote']: # if no vote and user wants to downvote
        vote = VoteClass(user_id=data['user_id'], item_id=item_id, upvote=False)
        db.session.add(vote)
    elif not vote.upvote and not data['downvote']: # if user downvoted and now wants to remove downvote
        db.session.delete(vote)
    elif vote.upvote and data['downvote']:  #if user upvoted and now wants to downvote
        vote.upvote = False
        db.session.add(vote)
    
    db.session.commit()

@bp.route("/threads/<int:thread_id>/upvote", methods=["POST"])
def thread_upvote(thread_id):
    print('reached')
    thread = db.get_or_404(Thread, thread_id)
    if thread.deleted:
        return Response(status=400, response=f"Thread with id {thread_id} has been deleted")
    
    handle_upvote(ThreadVote, thread_id)
    
    db.session.commit()
    return Response(status=200)

@bp.route("/threads/<int:thread_id>/downvote", methods=["POST"])
def thread_downvote(thread_id):
    print('reached')
    thread = db.get_or_404(Thread, thread_id)
    if thread.deleted:
        return Response(status=400, response=f"Thread with id {thread_id} has been deleted")
    
    handle_downvote(ThreadVote, thread_id)

    return Response(status=200)

@bp.route("/comments/<int:comment_id>/upvote", methods=["POST"])
def comment_upvote(comment_id):
    comment = db.get_or_404(Comment, comment_id)
    if comment.deleted:
        return Response(status=400, response=f"Comment with id {comment_id} has been deleted")
    
    handle_upvote(CommentVote, comment_id)
    
    return Response(status=200)

@bp.route("/comments/<int:comment_id>/downvote", methods=["POST"])
def comment_downvote(comment_id):
    comment = db.get_or_404(Comment, comment_id)
    if comment.deleted:
        return Response(status=400, response=f"Comment with id {comment_id} has been deleted")
    
    handle_downvote(CommentVote, comment_id)
    return Response(status=200)
