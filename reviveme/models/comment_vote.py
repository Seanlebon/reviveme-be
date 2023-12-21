from reviveme.db import db

class CommentVote(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey("threads.id"), primary_key=True)
    upvote = db.Column(db.Boolean, nullable=False) # true if upvote, false if downvote

    def __init__(self, user_id, comment_id, upvote):
        self.user_id = user_id
        self.comment_id = comment_id
        self.upvote = upvote
    
    def __repr__(self):
        return f"<CommentVote user_id={self.user_id!r}, thread_id={self.comment_id!r}, {'upvote' if self.upvote else 'downvote'}>"
