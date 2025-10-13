from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import func 

# ✅ Initialize SQLAlchemy here (NOT imported from app.py)
db = SQLAlchemy()

# ✅ Association table for likes
likes = db.Table(
    'likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('thought_id', db.Integer, db.ForeignKey('thought.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    liked_thoughts = db.relationship(
        'Thought', secondary='likes',
        back_populates='liked_by', lazy='dynamic'
    )
    def total_likes_received(self):
        total_likes=0

        for thought in self.thoughts:
            total_likes += len(thought.liked_by) # Use len() instead of thought.like_count()
        return total_likes
    
    def get_milestones(self):
        milestones = []
        if len(self.thoughts) >= 10:
            milestones.append("The Consistent Contributor (10+ Posts)")
        
        if self.total_likes_received() >= 50: 
            milestones.append("The Beloved Listener (50+ Total Likes)")
        return milestones

class Thought(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    mood = db.Column(db.String(50), nullable=True)

    user = db.relationship('User', backref=db.backref('thoughts', lazy=True))  # ✅ Add this

    liked_by = db.relationship(
        'User', secondary='likes',
        back_populates='liked_thoughts', lazy='select'
    )

    def is_liked_by(self, user):
        return user in self.liked_by

    def like_count(self):
        return len(self.liked_by) 

