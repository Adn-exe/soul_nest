from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from milestones import get_milestones 

db = SQLAlchemy()

# Association table for likes
likes = db.Table(
    'likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('thought_id', db.Integer, db.ForeignKey('thought.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    profile_image = db.Column(db.String(200), nullable=True)

    # Relationships
    liked_thoughts = db.relationship(
        'Thought', secondary='likes',
        back_populates='liked_by', lazy='dynamic'
    )

    # -------------------- Stats --------------------
    def total_likes_received(self):
        return sum(thought.liked_by.count() for thought in self.thoughts)

    # -------------------- External Milestones Call --------------------
    def get_milestones(self):
        return get_milestones(self)
    
    # --- Removed the internal calculate_streak and get_milestones methods ---


class Thought(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    mood = db.Column(db.String(50), nullable=True)

    # Relationships
    # Backref for 'thoughts' is now lazy=True (default) or lazy='select' 
    # to avoid having to call .all() inside total_likes_received.
    user = db.relationship('User', backref=db.backref('thoughts', lazy=True)) 
    liked_by = db.relationship(
        'User', secondary='likes',
        back_populates='liked_thoughts', lazy='dynamic' # Keep dynamic for efficiency
    )

    def is_liked_by(self, user):
        # Corrected to use dynamic filter
        return self.liked_by.filter(likes.c.user_id == user.id).first() is not None

    def like_count(self):
        # Corrected to use dynamic count
        return self.liked_by.count()