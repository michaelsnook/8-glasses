from datetime import datetime
import os, string
from flask import Flask, request, session, g
from flask.ext.sqlalchemy import SQLAlchemy
app = Flask(__name__)
import eightglasses.views

app.config.from_object(__name__)

# Load default config
app.config.update(dict(
  DEBUG=True,
  SECRET_KEY='development key',
  USERNAME='admin',
  PASSWORD='default'
))
app.config.from_envvar('EIGHTGLASSES_SETTINGS', silent=True)

#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/eightglasses'

#"""
# on heroku you have a database_url on os.environ
if hasattr(os.environ, 'DATABASE_URL'):
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
# for local database. change this in production
else:
  app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/eightglasses'
#"""

# now that we've config'd our app... get the db object
db = SQLAlchemy(app)
