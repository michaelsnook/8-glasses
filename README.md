Eight Glasses
=========

A simple app to track how many glasses of water I drink each day, and a project
to learn Python for the web.

It should be pretty easy to install on your own machine, if you like. Make a
PostgresSQL database with `createdb eightglasses`; clone the repository;
set up a virtual environment and activate it; run `pip install -r requirements.txt`; then launch with `python
runserver.py`. There's also a Procfile for Heroku, so if you have it, you can use `foreman start` to run the application via Gunicorn.

You can check out the most recent deployed public app at
http://eightglasses.herokuapp.com/. The daily and weekly queries don't work yet,
which are pretty core to the functionality desired, so it remains incomplete
until that's done.

Aside from that, the to-do list looks something like this:
* Add support and authentication for multiple user accounts. (Considering
  following [this advice](http://flask.pocoo.org/mailinglist/archive/2012/8/7/extending-flaskr-for-multiple-users/#bac23c687a882a3c234d63a7666b8b55).)
* Summary tables showing how you've been doing during past days/weeks (or else
  you can only see your progress for today or this week).
* Visualize multiple progress metrics, like the area graph in [this d3 example](http://bl.ocks.org/mbostock/1256572).
* ~~Figure out how to put it on the public web (probably through Heroku).~~ ([here](http://eightglasses.herokuapp.com))
* ~~Switch off SQLite to PostgreSQL and SQLAlchemy to abstract database operations.~~
* ~~Redo folder structure to use `__init__.py` along with `views.py` and `models.py`
instead of one monster file so I'm not writing like a barbarian anymore.~~
* Add fun / configurable messages of encouragement for when you do good things.
* Perhaps enable sharing on social media when you surpass a positive goal.
* I might make each section into a subtle progress bar. That could be neat.

In general, this has been a really fun application to write. I started with the
tutorial for [Flask](http://flask.pocoo.org/), an open source micro-framework
for Python. The html, css, and modals rely on [Foundation](http://foundation.zurb.com/),
(which uses [normalize.css](http://necolas.github.io/normalize.css/) and
[modernizr.js](http://modernizr.com/)), and colors from [clrs.cc](http://clrs.cc/).

So far the most frustrating thing was trying to make the application work on
Heroku. I had to become a lot more comfortable with the workings of my operating
system and my development environment, which is perhaps why I found it to be
such a valuable exercise.

That said, it was important to learn the whole range of pieces needed to set up
a prototype app. When I wrote the first version a year ago, I had never used
Flask, Foundation, SQLAlchemy, or Heroku before, but now I use them and tools
like them rather frequently for work and play. I'm looking forward to wrapping
up the original set of features so I can call it a day, or decide to plan some
more work on it. (I'm thinking about integrating with some of the fitness APIs.)
