from reviveme.db import db
from sqlalchemy.orm import synonym

class ThreadVote(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey("threads.id"), primary_key=True)
    upvote = db.Column(db.Boolean, nullable=False) # true if upvote, false if downvote

    item_id = synonym('thread_id')

    def __init__(self, user_id, item_id, upvote):
        self.user_id = user_id
        self.thread_id = item_id
        self.upvote = upvote
    
    def __repr__(self):
        return f"<ThreadVote user_id={self.user_id!r}, thread_id={self.thread_id!r}, {'upvote' if self.upvote else 'downvote'}>"
