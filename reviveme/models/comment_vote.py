from reviveme.db import db
from sqlalchemy.orm import synonym

class CommentVote(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"), primary_key=True)
    upvote = db.Column(db.Boolean, nullable=False) # true if upvote, false if downvote

    item_id = synonym('comment_id')

    def __init__(self, user_id, item_id, upvote):
        self.user_id = user_id
        self.comment_id = item_id
        self.upvote = upvote
    
    def __repr__(self):
        return f"<CommentVote user_id={self.user_id!r}, comment_id={self.comment_id!r}, {'upvote' if self.upvote else 'downvote'}>"
