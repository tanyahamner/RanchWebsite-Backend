from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID

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
import endpoints


def create_all():
    with app.app_context():
        db.create_all()

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

def validate_auth_token(auth_token):
    if auth_token is None or auth_token == "" or auth_token == 'not required':
        return False
    auth_record = db.session.query(AuthToken).filter(AuthToken.auth_token == auth_token).filter(AuthToken.expiration > datetime.utcnow()).first()
    
    return auth_record


@app.route("/organization/add", methods=["POST"])
def organization_add() -> Response:
    return endpoints.organization_add(request)

@app.route("/organization/update", methods=["POST"])
def organization_update() -> Response:
    return endpoints.organization_update(request)

@app.route("/organization/get")
def organizations_get_all() -> Response:
    return endpoints.organizations_get(request)

@app.route("/organization/get/<org_id>")
def organization_get_by_id(org_id) -> Response:
    return endpoints.organization_get_by_id(request, org_id)

@app.route("/organization/delete/<org_id>", methods=["DELETE"])
def organization_delete_by_id(org_id):
    return endpoints.organization_delete_by_id(request, org_id)

@app.route("/organization/activate/<org_id>", methods=["PUT"])
def organization_activate_by_id(org_id):
    return endpoints.organization_activate_by_id(request, org_id)

@app.route("/organization/deactivate/<org_id>", methods=["PUT"])
def organization_deactivate_by_id(org_id):
    return endpoints.organization_deactivate_by_id(request, org_id)
    
@app.route("/organization/search/<search_term>")
def organization_get_by_search(search_term, internal_call=False, p_auth_info=None):
     return endpoints.organization_get_by_search(request, search_term, internal_call, p_auth_info)

@app.route("/search/<search_term>")
def get_objects_by_search(search_term):
    # print(request)
    return endpoints.get_objects_by_search(request, search_term)

@app.route("/user/add", methods=["POST"])
def user_add():
    return endpoints.user_add(request, bcrypt)

@app.route("/user/update", methods=["POST"])
def user_update():
    return endpoints.user_update(request)

@app.route("/user/get", methods=["GET"])
def users_get_all():
    return endpoints.users_get_all(request)

@app.route("/user/get/<user_id>", methods=["GET"])
def user_get_by_id(user_id):
    return endpoints.user_get_by_id(request, user_id)

@app.route("/user/get/me", methods=["GET"])
def user_get_from_auth_token():
    return endpoints.user_get_from_auth_token(request)

@app.route("/user/get/organization/<org_id>", methods=["GET"])
def users_get_by_org_id(org_id):
    return endpoints.users_get_by_org_id(request, org_id)

@app.route("/user/delete/<user_id>", methods=["DELETE"])
def user_delete(user_id):
    return endpoints.user_delete(request, user_id)

@app.route("/user/activate/<user_id>", methods=["PUT"])
def user_activate(user_id):
    return endpoints.user_activate(request, user_id)

@app.route("/user/deactivate/<user_id>", methods=["PUT"])
def user_deactivate(user_id):
        return endpoints.user_deactivate(request, user_id)

@app.route("/user/search/<search_term>")
def users_get_by_search(search_term, internal_call=False, p_auth_info=None):
    return endpoints.users_get_by_search(request, search_term, internal_call, p_auth_info)

@app.route("/user/auth", methods=["POST"])
def auth_token_add():
    return endpoints.auth_token_add(request, bcrypt)

@app.route("/user/logout", methods=["PUT"])
def auth_token_remove():
    return endpoints.auth_token_remove(request)

@app.route("/user/pw_change_request", methods=["POST"])
def pw_change_request() -> Response:
    return endpoints.forgot_password.pw_change_request(request, active)

@app.route("/user/forgot_password_change", methods=["POST"])
def forgot_password_change(bcrypt) -> Response:
    return endpoints.forgot_password.forgot_password_change(request, bcrypt)

if __name__ == "__main__":
    app.run(debug=True)