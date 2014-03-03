Eight Glasses
=========

A simple app to track how many glasses of water I drink each day.

If you'd like to install it on your own machine, simply clone the repository to your local machine, activate a virtual environment, run `pip install -r requirements.txt`, and run with `python eightglasses.py`. 

The repository is set up with requirements.txt and a Procfile for deployment to Heroku. You can check out a recent deployment at http://vast-shelf-1754.herokuapp.com/ (but of course it doesn't work very well because I haven't upgraded to PostgreSQL).

There is a PostgreSQL / SQLAlchemy version in egalchemy.py, but I can't make the same promises about easy setup, and it's still not doing date or week filters, so the front page totals are all-time totals. 