from datetime import datetime
import os, string
from flask import Flask, request, session, g
from flask.ext.sqlalchemy import SQLAlchemy
app = Flask(__name__)

import eightglasses.views
app.config.from_object('default_settings')
#app.config.from_envvar('EIGHTGLASSES_SETTINGS', silent=True)
app.config.from_object('settings')
