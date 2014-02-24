from datetime import datetime 
import os, string
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object(__name__)

# Load default config
app.config.update(dict(
  DATABASE=os.path.join(app.root_path, 'egalchemy.db'),
  DEBUG=True,
  SECRET_KEY='development key',
  USERNAME='admin',
  PASSWORD='default'
))
# I don't know how this part works
app.config.from_envvar('EIGHTGLASSES_SETTINGS', silent=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///egalchemy.db'
db = SQLAlchemy(app)


class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True)
  email = db.Column(db.String(120), unique=True)
  
  def __init__(self, username, email):
    self.username = username
    self.email = email

  def __repr__(self):
    return '<User %r>' % self.username

class Goal(db.Model):
  __tablename__ = 'goals'
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.DateTime)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id')) 
  name = db.Column(db.String(20), nullable=True)
  goal = db.Column(db.Float, nullable=False)
  type = db.Column(db.String(20), default='increment')
  direction = db.Column(db.String(20), default='positive')
  period = db.Column(db.String(20), default='daily')
  verb = db.Column(db.String(20), nullable=True)
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
  created_at = db.Column(db.DateTime)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'))
  name = db.Column(db.String(20), nullable=False)
  total = db.Column(db.Float, default=1)
  notes = db.Column(db.String(120), nullable=True)

  def __init__(self, name, goal_id, total=1, notes=None):
    self.created_at = datetime.utcnow()
    self.name = name
    self.goal_id = goal_id
    self.total = total
    self.notes = notes

  def __repr__(self):
    return '<Name %r>' % self.name


@app.route('/')
def home():
  if not session.get('logged_in'):
    return render_template('index.html')
  entries = Entry.query.all()
  dailytotals = Goal.query.filter( Goal.period == 'daily' ).all()
  weeklytotals = Goal.query.filter( Goal.period == 'weekly' ).all()  
  goaltotals = dailytotals + weeklytotals
  
  return render_template('alhome.html', entries=entries, goaltotals=goaltotals, )
    
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
 
  return render_template('aladmin.html', entries=entries, goals=goals, )

@app.route('/numbers')
def numbers():
  """ 
  "  This is where I'll be working on improvement-over-time charts and visualizations.
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
  if True:
#  if db.total_changes:
    flash('New entry was successfully posted')
  else:
    flash('Entry not added')
  return redirect(url_for('home'))

@app.route('/removeentry', methods=['POST'])
def remove_entry():
  if not session.get('logged_in'):
    abort(401)
  form = request.form
  if form['delete'] == 'delete' and form['areyousure']:
    s = ''
    for f in form:
      if f[:2] == 'id':
        s = s + f[3:] + ','
    s = s[:-1]
    # i don't know if this will work
    app.logger.debug(s)
    entrytarget = Entry.query.filter( Entry.id.in_((s)) ).all()
    for t in entrytarget:
      db.session.delete(t)
    db.session.commit()
    flash('Successfully deleted those pesky entries')
    return redirect(url_for('home'))
  else:
    flash('Something went wrong with the form and your goal was not removed')
    return redirect(url_for('home'))

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
  return redirect(url_for('admin'))   
    
@app.route('/removegoal', methods=['POST'])
def remove_goal():
  if not session.get('logged_in'):
    abort(401)
  form = request.form
  if form['delete'] == 'delete' and form['areyousure']:
    s = form['id_name'].split(',')
    
    target = Goal.query.filter( Goal.id == s[0] , Goal.name == s[1] ).first()
    """ @@TODO: set up cascading deletes to get the entries too """
    db.session.delete(target)
    db.session.commit()
    flash('Your goal was successfully deleted :(')
    return redirect(url_for('home'))
  else:
    flash('Something went wrong with the form and your goal was not removed')
    return redirect(url_for('home'))

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