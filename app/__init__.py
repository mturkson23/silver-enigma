# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

import os

from flask            import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login      import LoginManager
from flask_bcrypt     import Bcrypt
from .prefixmiddleware import PrefixMiddleware

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config.from_object('app.configuration.Config')

app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix="/psalm2vs8")

db = SQLAlchemy  (app) # flask-sqlalchemy
bc = Bcrypt      (app) # flask-bcrypt

lm = LoginManager(   ) # flask-loginmanager
lm.init_app(app) # init the login manager
lm.login_view = "login"

# Setup database
@app.before_first_request
def initialize_database():
    db.create_all()

TEMPLATES_AUTO_RELOAD = True

# Import routing, models and Start the App
from app import views, models
