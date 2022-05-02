from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import sys

from flask_bcrypt import Bcrypt
from flask_cors import CORS
import uuid
from db import db, init_db
from flask_marshmallow import Marshmallow

from models.organizations import organization_schema, organizations_schema, Organization, OrganizationSchema
from models.app_users import user_schema, users_schema, AppUser, AppUserSchema
from models.auth_tokens import auth_token_schema, AuthToken, AuthTokenSchema

from util.validate_uuid4 import validate_uuid4
from util.foundation_utils import strip_phone

import os
from os.path import abspath, dirname, isfile, join
from datetime import datetime, timedelta
from util.date_range import DateRange
import routes


def create_all():
    with app.app_context():
        db.create_all()
        # Echoing the command-line parameters
        for arg in range(len(sys.argv[1:])):
            print(sys.argv[arg + 1])

        # Create DevPipeline Organization
        print("Querying for DevPipeline organization...")
        org_data = db.session.query(Organization).filter(Organization.name == "DevPipeline").first()
        if org_data == None:
            print("DevPipeline organization not found. Creating DevPipeline Organization in database...")
            name = 'DevPipeline'
            address = '518 East 800 North, Suite C'
            city = 'Orem'
            state = 'Utah'
            zip_code = '84097'
            phone = '3853090807'
            active = True
            created_date = datetime.now()
            
            org_data = Organization(name, address, city, state, zip_code, phone, created_date, active)

            db.session.add(org_data)
            db.session.commit()
        else:
            print("DevPipeline Organization found!")
        
        
        # Create default super-admin user
        print("Querying for Super Admin user...")
        user_data = db.session.query(AppUser).filter(AppUser.email == 'foundation-admin@devpipeline.com').first()
        if user_data == None:
            print("Super Admin not found! Creating foundation-admin@devpipeline user...")
            first_name = 'Super'
            last_name = 'Admin'
            email = 'foundation-admin@devpipeline.com'
            newpw = ''
            while newpw == '' or newpw is None:
                newpw = input(' Enter a password for Super Admin:')

            #password = 'N01t4dnU0f'
            password = newpw
            phone = '3853090807'
            active = True
            org_id = org_data.org_id
            created_date = datetime.now()
            role = 'super-admin'
            
            hashed_password = bcrypt.generate_password_hash(password).decode("utf8")
            record = AppUser(first_name, last_name, email, hashed_password, phone, created_date, org_id, role, active)

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
#  TODO: database url needs to be in env variable
   database_host = "127.0.0.1:5432"
   database_name = "foundation"
   app.config['SQLALCHEMY_DATABASE_URI'] = f'postgres://{database_host}/{database_name}'
   app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
   
   init_db(app, db)

   current_dir = dirname(abspath(__file__))
   if config_file is None:
      config_file = abspath(join(current_dir, '../config/config.yml'))
   else:
      config_file = abspath(config_file)
   
   # raise error if config_file cannot be found
#    if not isfile(config_file):
#       raise EnvironmentError(f"App config file does not exist at {config_file}")

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

def validate_auth_token(auth_token):
    if auth_token is None or auth_token == "" or auth_token == 'not required':
        return False
    auth_record = db.session.query(AuthToken).filter(AuthToken.auth_token == auth_token).filter(AuthToken.expiration > datetime.utcnow()).first()
    
    return auth_record

if __name__ == "__main__":
    create_all()
    app.run(debug=True)