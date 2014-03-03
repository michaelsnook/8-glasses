from datetime import datetime 
import os, string
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object(__name__)

# Load default config
app.config.update(dict(
  DEBUG=True,
  SECRET_KEY='development key',
  USERNAME='admin',
  PASSWORD='default'
))
app.config.from_envvar('EIGHTGLASSES_SETTINGS', silent=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/eightglasses'
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

@app.route('/')
def home():
    if not session.get('logged_in'):
      return render_template('index.html')    
    both_text = db.text(
      "select max(entries.id) as max_entry_id, max(entries.created_at) as most_recent, "
      "goals.id as goal_id, goals.name, goals.type, goals.direction, goals.period, goals.verb, "
      "goals.subtitle, sum(coalesce(entries.total, 0)) as sum, count(distinct entries.id) as count, "
      "goals.goal, goals.created_at from goals left join entries on (entries.name=goals.name) "
      "group by goals.name, goals.id "    
    )    
    goaltotals = db.engine.execute(both_text)
    return render_template('alhome.html', goaltotals=goaltotals)

    
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
  return redirect(url_for('admin'))   

    
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
    db.session.delete(target)
    db.session.commit()
    flash('Your goal was successfully deleted :(')
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