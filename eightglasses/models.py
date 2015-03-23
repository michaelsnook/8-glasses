from datetime import datetime
import os, string
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from eightglasses import app

db = SQLAlchemy(app)

#class User(db.Model):
#  """ The User model... not currently in use """
#
#  __tablename__ = 'users'
#  id = db.Column(db.Integer, primary_key=True)
#  username = db.Column(db.String(80), unique=True)
#  email = db.Column(db.String(120), unique=True)
#
#  def __init__(self, username, email):
#    self.username = username
#    self.email = email
#
#  def __repr__(self):
#    return '<User %r>' % self.username

class Goal(db.Model):

  """ Users typically have a handful of goals each. Each goal has a numeric
  success measure and a time interval which are used to give feedback to the
  user on whether they are meeting their goals. """

  __tablename__ = 'goals'
  id = db.Column(db.Integer, primary_key=True)

  # set automatically
  created_at = db.Column(db.DateTime, default="current_timestamp")

  # not currently in use
  #user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

  # the most important text field!
  name = db.Column(db.String(20), nullable=True)

  # how many?
  goal = db.Column(db.Float, nullable=False)

  # increment, count, or float.
  type = db.Column(db.String(20), default='increment')

  # options are positive or negative, meaning things you want to do less of
  direction = db.Column(db.String(20), default='positive')

  # right now only daily and weekly goals are supported
  period = db.Column(db.String(20), default='daily')

  # optional. just for fun. DRINK eight glasses. DO sixty situps.
  verb = db.Column(db.String(20), nullable=True)

  # meh
  subtitle = db.Column(db.String(40), nullable=True)

  def __init__(self, name, goal, type='increment', direction='positive',
                            period='daily', verb=None, subtitle=None):
    self.created_at = datetime.utcnow()
    self.name = name
    self.goal = goal
    self.type = type
    self.direction = direction
    self.period = period
    self.verb = verb
    self.subtitle = subtitle

  def __repr__(self):
    return '<Goal %r>' % self.name


class Entry(db.Model):
  __tablename__ = 'entries'
  id = db.Column(db.Integer, primary_key=True)

  # set automatically
  created_at = db.Column(db.DateTime, default="current_timestamp")

  # not in use
  #user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

  # the foreign key
  goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'))
  #@@TODO add a backref

  # the main text label
  name = db.Column(db.String(20), nullable=False)

  # how many of the thing are we logging with this action?
  total = db.Column(db.Float, default=1)

  # unused
  notes = db.Column(db.String(120), nullable=True)

  def __init__(self, name, goal_id, total, notes=None):
    self.created_at = datetime.utcnow()
    self.name = name
    self.goal_id = goal_id
    self.total = total
    self.notes = notes

  def __repr__(self):
    return '<Entry %r>' % self.name
