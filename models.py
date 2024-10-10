# models.py
from flask_login import UserMixin
from db import db
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    submissions = db.relationship("Submission", backref="user", lazy=True)

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    hint = db.Column(db.Text, nullable=True)
    answer_info = db.Column(db.Text, nullable=True)
    flag = db.Column(db.String(100), nullable=False)  # The correct answer
    submissions = db.relationship("Submission", backref="challenge", lazy=True)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenge.id"), nullable=False)
    submitted_flag = db.Column(db.String(100), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class GlobalSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    limit_submissions = db.Column(db.Boolean, default=False)
