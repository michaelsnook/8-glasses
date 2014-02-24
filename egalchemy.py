import os, string
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime 

app = Flask(__name__)
app.config.from_object(__name__)

#load default config
app.config.update(dict(
  DATABASE=os.path.join(app.root_path, 'eightglasses.db'),
  DEBUG=True,
  SECRET_KEY='development key',
  USERNAME='admin',
  PASSWORD='default'
))
app.config.from_envvar('EIGHTGLASSES_SETTINGS', silent=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskr.db'

db = SQLAlchemy(app)

#def connect_db():
#    """Connects to the specific database."""
#    rv = sqlite3.connect(app.config['DATABASE'])
#    rv.row_factory = sqlite3.Row
#    return rv

#def get_db():
#    """Opens a new database connection if there is none yet for the
#    current application context.
#    """
#    if not hasattr(g, 'sqlite_db'):
#        g.sqlite_db = connect_db()
#    db = g.sqlite_db
#    with app.open_resource('scripts/schema_make.sql', mode='r') as f:
#      db.cursor().executescript(f.read())
#    db.commit() 
#    return db

# @app.teardown_appcontext
# def close_db(error):
#    """Closes the database again at the end of the request."""
#    if hasattr(g, 'sqlite_db'):
#        g.sqlite_db.close()

#def init_db():
#    with app.app_context():
#        db = get_db()
#        with app.open_resource('scripts/schema.sql', mode='r') as f:
#            db.cursor().executescript(f.read())
#        db.commit()

""" @@TODO: this function is really not supposed to still be here """
def clear_entries():
    with app.app_context():
#        db = get_db()
        with app.open_resource('scripts/clear.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit() 


@app.route('/')
def home():
    if not session.get('logged_in'):
      return render_template('index.html')
#    db = get_db()
    cur = db.execute('select id, name, total, type, datetime(created_at, "localtime") `created_at`, notes from entries order by id desc')
    entries = cur.fetchall()
    
    """ I'm structuring these queries to share the same "start" and "end" strings, so that it's 
        extra super clear what exactly is varying from one to the next.
        
        It's set up to enforce the same exact SELECT structure so the lists can be appended together
        arbitrarily, but the app mostly relies on the combination of the daily and weekly queries
        which never select the same rows as one another and together select the entire set.
        
        @@TODO: upgrade to SQLAlchemy (?)
        
        """
    querystart = 'select max(entries.id) `max_entry_id`, datetime(max(entries.created_at), "localtime") `most_recent`, goals.id `goal_id`, goals.name, goals.type, goals.direction, goals.period, goals.verb, goals.subtitle, sum(coalesce(entries.total, 0)) `sum`, count(distinct entries.id) `count`, goals.goal,  datetime(goals.created_at, "localtime") `created_at` from goals left join entries on '
    queryend = 'group by goals.name'
    
    cur_day = db.execute(querystart + '(entries.name=goals.name and date(entries.created_at, "localtime") = date("now", "localtime")) where goals.period="daily" ' + queryend)
    dailytotals = cur_day.fetchall()

    cur_week = db.execute(querystart + '(entries.name=goals.name and date(entries.created_at, "localtime", "weekday 1", "-7 days") = date("now", "localtime", "weekday 1", "-7 days")) where goals.period="weekly" ' + queryend)
    weeklytotals = cur_week.fetchall()

    cur = db.execute(querystart + '(entries.name=goals.name) ' + queryend + ', goals.type order by goals.created_at asc')
    totals = cur.fetchall()
    
    goaltotals = dailytotals + weeklytotals
    
    return render_template('home.html', entries=entries, goaltotals=goaltotals, totals=totals)
    
@app.route('/admin')
def admin():
    """ Provides an easy interface for viewing all entries and deleting entries if needed. 
        It's not a substitute for a real admin, and I notice that flask does have an Admin 
        tool I could check out. But I'm not sure if users really need a full admin, and I'd
        kind of rather go through the work of building it myself to know that I'm doing 
        things in a way that will still feel good on a phone.
    
     """

    if not session.get('logged_in'):
        abort(401)
#    db = get_db()
    
    """ This one just returns every entry. """
    cur = db.execute('select id, name, total, type, created_at, notes from entries order by id desc')
    entries = cur.fetchall()

    """ This one returns all-time totals for every goal. """
    cur = db.execute('select goals.id `goal_id`, goals.name, goals.type, goals.direction, goals.period, goals.verb, goals.subtitle, sum(coalesce(entries.total, 0)) `sum`, count(distinct entries.id) `count`, goals.goal, max(entries.created_at) `most_recent`, goals.created_at from goals left join entries on (entries.name=goals.name) group by goals.name, goals.type order by goals.created_at asc')
    totals = cur.fetchall()

    return render_template('admin.html', entries=entries, totals=totals, )

@app.route('/numbers')
def numbers():
    if not session.get('logged_in'):
        abort(401)
#    db = get_db()
    cur = db.execute('select id, name, total, type, created_at, notes from entries order by id desc')
    entries = cur.fetchall()
    return render_template('numbers.html', entries=entries, )


@app.route('/addentry', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
#    db = get_db()
    form = request.form

    db.execute('insert into entries (name, total, notes) values (?, ?, ?)',
                 [form['name'], form['total'], form['notes']])
    db.commit()
    app.logger.debug(db.total_changes)
    if db.total_changes:
      flash('New entry was successfully posted')
    else:
      flash('Entry not added')
    return redirect(url_for('home'))

@app.route('/removeentry', methods=['POST'])
def remove_entry():
    if not session.get('logged_in'):
        abort(401)
#    db = get_db()
    form = request.form
    if form['delete'] == 'delete' and form['areyousure']:
      s = ''
      for f in form:
        if f[:2] == 'id':
          s = s + f[3:] + ','
      s = s[:-1]
      db.execute('DELETE FROM entries WHERE id in(' + s + ')')
      db.commit()
      flash('Successfully deleted those pesky entries')
      return redirect(url_for('home'))
    else:
      flash('Something went wrong with the form and your goal was not removed')
      return redirect(url_for('home'))



@app.route('/addgoal', methods=['POST'])
def add_goal():
    if not session.get('logged_in'):
        abort(401)
#    db = get_db()
    form = request.form
    db.execute('insert into goals (name, goal, type, direction, period, verb, subtitle) values (?, ?, ?, ?, ?, ?, ?)',
                 [form['name'], form['goal'], form['type'], form['direction'], form['period'], form['verb'], request.form['subtitle']])
    db.commit()
    flash('Your new goal was successfully added!')
    return redirect(url_for('home'))
    
    
@app.route('/removegoal', methods=['POST'])
def remove_goal():
    if not session.get('logged_in'):
        abort(401)
#    db = get_db()
    form = request.form
    if form['delete'] == 'delete' and form['areyousure']:
      s = form['id_name'].split(',')
      db.execute('DELETE FROM goals WHERE id = ? AND name = ?', [s[0], s[1]])
      db.commit()
      db.execute('DELETE FROM entries where name = ?', [s[1]])
      db.commit()
      flash('Your goal was successfully deleted :(')
      return redirect(url_for('home'))
    else:
      flash('Something went wrong with the form and your goal was not removed')
      return redirect(url_for('home'))



@app.route('/login', methods=['GET', 'POST'])
def login():
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
