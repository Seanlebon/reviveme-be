from reviveme import db

class Vote(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    upvote = db.Column(db.Boolean, nullable=False)