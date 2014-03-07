### This is an example settings file. It's actually identical to the settings file I
### use on my local machine, but I figured some people would want different settings
### files, so i left settings.py in .gitignore and added this.
###
### The app is built primarily for heroku, so I just don't deploy this file and the
### app fails to load SETTINGS so it falls bake to heroku's DATABASE_URL. This way
### it runs the same on my local machine and on heroku.
###
### @@TODO: Figure out if there's a more self-explanatory way of doing all this.

import os, string

SETTINGS = dict(
  db_local = 'postgresql://localhost/eightglasses'
)
