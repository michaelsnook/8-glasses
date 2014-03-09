Eight Glasses
=========

A simple app to track how many glasses of water I drink each day, and a project to learn Python for the web.

It should be pretty easy to install on your own machine, if you like. Make a PostgresSQL database with `createdb eightglasses`; clone the repository; activate a virtual environment; `pip install -r requirements.txt`; `python eightglasses.py`. There's also a Procfile for Heroku or, if you have it installed, `foreman start` will also run the application via Gunicorn. 

You can check out the most recent deployed public app at http://eightglasses.herokuapp.com/. The daily and weekly queries don't work yet (SQLite was actually much more convenient for my specific use case!). There is a once-functioning SQLite version in eglite.py, but only to show the raw queries whose behavior I'm trying to replicate in SQLAlchemy/PostgreSQL.

Aside from that, the to-do list looks something like this:
* Add support and authentication for multiple user accounts.
* Summary tables showing how you've been doing during past days/weeks (or else you can only see your progress for today or this week).
* Visualize multiple progress metrics, like the area graph in [this d3 example](http://bl.ocks.org/mbostock/1256572).
* ~~Figure out how to put it on the public web (probably through Heroku).~~ ([here](http://eightglasses.herokuapp.com))
* ~~Switch off SQLite to PostgreSQL and SQLAlchemy to abstract database operations.~~
* Add fun / configurable messages of encouragement for when you do good things.
* Perhaps enable sharing on social media when you surpass a positive goal.
* I might make each section into a subtle progress bar. That could be neat.

In general, this has been a really fun application to write. I started with the tutorial for [Flask](http://flask.pocoo.org/), an open source micro-framework for Python. The html, css, and modals rely on [Foundation](http://foundation.zurb.com/), (which uses [normalize.css](http://necolas.github.io/normalize.css/) and [modernizr.js](http://modernizr.com/)), and colors from [clrs.cc](http://clrs.cc/).

So far the most frustrating thing has been trying to make the application work on Heroku. I'm already new with SQLAlchemy and am not used to having to set up or be in charge of a local database (things like `manage.py` always have felt like voodoo), and trying to troubleshoot in Heroku seems to be its own kind of thought process that requires a bunch of context awareness with things I'm new at. 

That said, it was important to me to learn the whole range of setting up a prototype app. I had never used Flask, Foundation, SQLAlchemy, or Heroku before, but now I think I could use them to make really quick prototypes of a number of different application concepts and end up with a simple, pretty, publicly accessible application in just a few days.

I've yet to figure out how I'm going to handle multiple user accounts. (Considering following [this advice](http://flask.pocoo.org/mailinglist/archive/2012/8/7/extending-flaskr-for-multiple-users/#bac23c687a882a3c234d63a7666b8b55).)