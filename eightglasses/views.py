from datetime import datetime
import os, string
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy
from eightglasses import app
import eightglasses.models
from eightglasses.models import Entry, Goal

db = SQLAlchemy(app)

@app.route('/')
def home():
  if not session.get('logged_in'):
    return render_template('index.html')
  both_text = db.text(
    "select max(entries.id) as max_entry_id, max(entries.created_at) as most_recent, "
    "goals.id as goal_id, goals.name, goals.type, goals.direction, goals.period, goals.verb, "
    "goals.subtitle, sum(coalesce(entries.total, 0)) as sum, count(distinct entries.id) as count, "
    "goals.goal, goals.created_at from goals left join entries on (entries.name=goals.name) "
    "where goals.period='daily' "
    "group by goals.name, goals.id "
    "UNION "
    "select max(entries.id) as max_entry_id, max(entries.created_at) as most_recent, "
    "goals.id as goal_id, goals.name, goals.type, goals.direction, goals.period, goals.verb, "
    "goals.subtitle, sum(coalesce(entries.total, 0)) as sum, count(distinct entries.id) as count, "
    "goals.goal, goals.created_at from goals left join entries on (entries.name=goals.name) "
    "where goals.period='weekly' "
    "group by goals.name, goals.id"
  )
  goaltotals = db.engine.execute(both_text)
  entries = Entry.query.order_by(Entry.id).all()
  goals = Goal.query.order_by(Goal.id).all()
  return render_template('home.html', goaltotals=goaltotals, totlas=goaltotals, entries=entries, goals=goals)


@app.route('/admin')
def admin():
  """
  "  Provides an easy interface for viewing all entries and deleting entries if needed.
  "  It's not a substitute for a real admin, and I notice that flask does have an Admin
  "  tool I could check out. But I'm not sure if users really need a full admin, and I'd
  "  kind of rather go through the work of building it myself to know that I'm doing
  "  things in a way that will still feel good on a phone.
  """
  if not session.get('logged_in'):
      abort(401)
  entries = Entry.query.order_by(Entry.id).all()
  goals = Goal.query.order_by(Goal.id).all()
  return render_template('admin.html', entries=entries, goals=goals, )

@app.route('/numbers')
def numbers():
  """
  " WIP
  "
  " This is where I'll be working on improvement-over-time charts and visualizations.
  """
  if not session.get('logged_in'):
    abort(401)
  entries = Entry.query.all()
  return render_template('numbers.html', entries=entries, )

@app.route('/addentry', methods=['POST'])
def add_entry():
  if not session.get('logged_in'):
    abort(401)
  form = request.form
  entry = Entry(form['name'], form['goal_id'], form['total'], form['notes'])
  db.session.add(entry)
  db.session.commit()
#  app.logger.debug(db.total_changes)
#  if True:
#  if db.total_changes:
  flash('New entry was successfully posted')
#  else:
#    flash('Entry not added')
  return redirect(url_for('home'))

@app.route('/removeentry', methods=['POST'])
def remove_entry():
  if not session.get('logged_in'):
    abort(401)
  form = request.form
  if form['delete'] == 'delete' and form['areyousure']:
    s = list()
    app.logger.debug(form)
    for f in form:
      if f[:2] == 'id':
        e = Entry.query.filter(Entry.id==form[f]).first()
        db.session.delete(e)
    db.session.commit()
    flash('Successfully deleted those pesky entries')
    return redirect(url_for('admin'))
  else:
    flash('Something went wrong with the form and your goal was not removed')
    return redirect(url_for('admin'))

@app.route('/addgoal', methods=['POST'])
def add_goal():
  if not session.get('logged_in'):
    abort(401)
  form = request.form
  goal = Goal(form['name'], form['goal'], form['type'],
    form['direction'], form['period'], form['verb'], form['subtitle'])
  db.session.add(goal)
  db.session.commit()
  flash('Your new goal was successfully added!')
  return redirect(url_for('home'))


@app.route('/removegoal', methods=['POST'])
def remove_goal():
  """ Provides a way to remove or delete goals """
  if not session.get('logged_in'):
    abort(401)
  form = request.form
  if form['delete'] == 'delete' and form['areyousure']:
    s = form['id_name'].split(',')
    target = Goal.query.filter( Goal.id == s[0] , Goal.name == s[1] ).first_or_404()
    """ @@TODO: set up cascading deletes to get the entries too """
    try:
      db.session.delete(target)
      db.session.commit()
      flash('Your goal was successfully deleted :(')
      return redirect(url_for('admin'))
    except:
      flash('Your goal could not be deleted. better keep at it.')
      return redirect(url_for('admin'))
  else:
    flash('Something went wrong with the form and your goal was not removed')
    return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
  """ successful login drops you onto the home page.  """
  """ @@TODO: add support for ?next=                  """
  error = None
  if request.method == 'POST':
    if request.form['username'] != app.config['USERNAME']:
      error = 'Invalid username'
    elif request.form['password'] != app.config['PASSWORD']:
      error = 'Invalid password'
    else:
      session['logged_in'] = True
      flash('You were logged in')
      return redirect(url_for('home'))
  return render_template('login.html', error=error)

@app.route('/logout')
def logout():
  session.pop('logged_in', None)
  flash('You were logged out')
  return redirect(url_for('home'))

if __name__ == '__main__':
  app.run()
