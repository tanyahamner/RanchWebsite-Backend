from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import sys

from flask_bcrypt import Bcrypt
from flask_cors import CORS
from db import db, init_db
from flask_marshmallow import Marshmallow

from models.organizations import Organizations
from models.app_users import AppUsers
from models.auth_tokens import AuthTokens

from util.validate_uuid4 import validate_uuid4
from util.foundation_utils import strip_phone

import os
from os.path import abspath, dirname, join
from datetime import datetime
import routes
import config

def create_all():
    with app.app_context():
        db.create_all()
        for arg in range(len(sys.argv[1:])):
            print(sys.argv[arg + 1])

        print("Querying for DevPipeline organization...")
        org_data = db.session.query(Organizations).filter(Organizations.name == "DevPipeline").first()
        if org_data == None:
            print("DevPipeline organization not found. Creating DevPipeline Organization in database...")
            
            active = True
            created_date = datetime.now()
            
            org_data = Organizations(config.org_name, config.org_address, config.org_city, config.org_state, config.org_zip_code, config.org_phone, created_date, active)

            db.session.add(org_data)
            db.session.commit()
        else:
            print("DevPipeline Organization found!")
        
        print("Querying for Super Admin user...")
        user_data = db.session.query(AppUsers).filter(AppUsers.email == config.su_email).first()
        if user_data == None:
            print(f"Super Admin not found! Creating Super Admin user ({config.su_email})...")
            
            newpw = ''
            while newpw == '' or newpw is None:
                newpw = input(' Enter a password for Super Admin:')
            password = newpw
            org_id = org_data.org_id
            role = 'super-admin'
            
            hashed_password = bcrypt.generate_password_hash(password).decode("utf8")
            record = AppUsers(first_name=config.su_first_name, last_name=config.su_last_name, email=config.su_email, phone=config.su_phone, password=hashed_password, org_id=org_id, role=role, active=True)

            db.session.add(record)
            db.session.commit()
        else:
            print("Super Admin user found!")

def create_app(config_file=None):
   """
   Default application factory

   Default usage:
      app = create_app()

   Usage with config file:
      app = create_app('/path/to/config.yml')

   If config_file is not provided, will look for default
   config expected at '<proj_root>/config/config.yml'.
   Returns Flask app object.
   Raises EnvironmentError if config_file cannot be found.
   """
   app = Flask(__name__)
   database_host = "127.0.0.1:5432"
   database_name = config.database_name
   app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI", f'postgres://{database_host}/{database_name}')
   app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
   
   init_db(app, db)

   current_dir = dirname(abspath(__file__))
   if config_file is None:
      config_file = abspath(join(current_dir, '../config/config.yml'))
   else:
      config_file = abspath(config_file)

   """ Setup helpful app attributes for determining whether an app is running
   in PRODUCTION, DEBUG OR DEV

   With this in place, it is possible to make simple checks in code for app state:

   from flask import current_app as app

   # inside some code block somewhere
   if app.live:
      # do live-only stuff here

   if app.debug:
      # do debug stuff

   if app.testing:
      # do something that should only happen during tests
      
   """
   cfg = app.config
   app.env = cfg.get('ENVIRONMENT', 'development')
   if app.debug:
      app.live = False
      if app.env == 'test':
         app.testing = True
      elif app.env == 'development':
         app.dev = True
      else:
         raise EnvironmentError('Invalid environment for app state. (Look inside __init__.py for help)')
   else:
      if app.env == 'production':
         app.live = True
      elif app.env == 'development':
         app.live = False
         app.testing = False
      else:
         raise EnvironmentError('Invalid environment for app state. (Look inside __init__.py for help)')
   return app


app = create_app()
bcrypt = Bcrypt(app)
CORS(app)
ma  = Marshmallow(app)

app.register_blueprint(routes.auth)
app.register_blueprint(routes.images)
app.register_blueprint(routes.orgs)
app.register_blueprint(routes.search)
app.register_blueprint(routes.users)


if __name__ == "__main__":
    create_all()
    app.run(debug=True)