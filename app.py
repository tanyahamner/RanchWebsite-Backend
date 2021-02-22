from flask import Flask, request, jsonify
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


def create_all():
    with app.app_context():
        db.create_all()

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
   database_name = "app"
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
def insert_organization():
    if request.content_type == "application/json":
        auth_info = validate_auth_token(request.headers.get("auth_token"))
        if not auth_info:
            return jsonify("Access Denied"), 401

        post_data = request.get_json()
        name = post_data.get('name')
        address = post_data.get('address')
        city = post_data.get('city')
        state = post_data.get('state')
        zip_code = post_data.get('zip_code')
        phone = post_data.get('phone')
        active = post_data.get('active')
        created_date = datetime.now()
        if active == None:
            active = True

        stripped_phone = strip_phone(phone)
        org_data = Organization(name, address, city, state, zip_code, stripped_phone, created_date, active)

        db.session.add(org_data)
        db.session.commit()

        return jsonify(organization_schema.dump(org_data)), 201
    else:
        return jsonify("ERROR: request must be in JSON format"), 400

@app.route("/organization/update", methods=["POST"])
def update_organization():
    if request.content_type == "application/json":
        auth_info = validate_auth_token(request.headers.get("auth_token"))
        if not auth_info:
            return jsonify("Access Denied"), 401

    if request.content_type == "application/json":
        post_data = request.get_json()
        org_id = post_data.get("org_id")
        if org_id == None:
            return jsonify("ERROR: org_id missing"), 400
        name = post_data.get('name')
        address = post_data.get('address')
        city = post_data.get('city')
        state = post_data.get('state')
        zip_code = post_data.get('zip_code')
        phone = post_data.get('phone')
        active = post_data.get('active')
        if active == None:
            active = True

        org_data = db.session.query(Organization).filter(Organization.org_id == org_id).first()
        org_data.name = name
        org_data.address = address
        org_data.city = city
        org_data.state = state
        org_data.zip_code = zip_code
        org_data.phone = strip_phone(phone)
        org_data.active = active

        db.session.commit()

        return jsonify(organization_schema.dump(org_data)), 200
    else:
        return jsonify("ERROR: request must be in JSON format"), 400

@app.route("/organization/get")
def get_all_organizations():
    auth_info = validate_auth_token(request.headers.get("auth_token"))
    if not auth_info:
        return jsonify("Access Denied"), 401

    all_organizations = []

    if auth_info.user.role != 'super-admin':
        all_organizations = db.session.query(Organization).filter(Organization.org_id == auth_info.user.org_id).order_by(Organization.name.asc()).all()
    else:
        all_organizations = db.session.query(Organization).order_by(Organization.name.asc()).all()
    
    return jsonify(organizations_schema.dump(all_organizations))

@app.route("/organization/get/<org_id>")
def get_organization_by_id(org_id):
    auth_info = validate_auth_token(request.headers.get("auth_token"))
    if not auth_info:
        return jsonify("Access Denied"), 401

    if validate_uuid4(org_id) == False:
        return jsonify("Invalid org ID"), 404

    org_query = db.session.query(Organization).filter(Organization.org_id == org_id)

    if auth_info.user.role != 'super-admin':
        org_query = org_query.filter(Organization.org_id == auth_info.user.org_id)
    
    org_data = org_query.first()

    if org_data:
        return jsonify(organization_schema.dump(org_data))

    return jsonify(f"Organization with org_id {org_id} not found"), 404

@app.route("/organization/delete/<org_id>", methods=["DELETE"])
def delete_organization(org_id):
    if request.content_type == "application/json":
        auth_info = validate_auth_token(request.headers.get("auth_token"))
        if not auth_info or auth_info.user.role != 'super-admin':
            return jsonify("Access Denied"), 401

        if validate_uuid4(org_id) == False:
            return jsonify("Invalid org ID"), 404

        if org_id == auth_info.user.org_id:
            return jsonify("Access Denied: You cannot delete your own organization"), 401

        org_data = db.session.query(Organization).filter(Organization.org_id == org_id).first()
        
        if org_data:
            db.session.delete(org_data)
            db.session.commit()
            return jsonify(f'Organization with org_id {org_id} deleted'), 201

        
        return jsonify(f'Organization with org_id {org_id} not found'), 404
    
    return jsonify("ERROR: request must be in JSON format"), 400

@app.route("/organization/activate/<org_id>", methods=["PUT"])
def activate_organization(org_id):
    if request.content_type == "application/json":
        auth_info = validate_auth_token(request.headers.get("auth_token"))
        if not auth_info:
            return jsonify("Access Denied"), 401

        if validate_uuid4(org_id) == False:
            return jsonify("Invalid org ID"), 404

        org_data = db.session.query(Organization).filter(Organization.org_id == org_id).first()
        if org_data:
            org_data.active = True
            db.session.commit()
            return jsonify(organization_schema.dump(org_data)), 200

        return jsonify(f'Organization with org_id {org_id} not found'), 404
    
    return jsonify("ERROR: request must be in JSON format"), 400

@app.route("/organization/deactivate/<org_id>", methods=["PUT"])
def deactivate_organization(org_id):
    if request.content_type == "application/json":
        auth_info = validate_auth_token(request.headers.get("auth_token"))
        if not auth_info or auth_info.user.role != 'super-admin':
            return jsonify("Access Denied"), 401

        if validate_uuid4(org_id) == False:
            return jsonify("Invalid org ID"), 404

        if org_id == auth_info.user.org_id:
            return jsonify("Access Denied: You cannot delete your own organization"), 401
        
        org_data = db.session.query(Organization).filter(Organization.org_id == org_id).first()
        if org_data:
            org_data.active = False
            db.session.commit()

            # Remove all auth records for anyone from that company
            auth_record_query = db.session.query(AuthToken)\
                .join(AppUser, AuthToken.user_id == AppUser.user_id)\
                .filter(AppUser.org_id == org_id)
            
            auth_records = auth_record_query.all()
            for auth_record in auth_records:
                db.session.delete(auth_record)

            db.session.commit()

            return jsonify(organization_schema.dump(org_data)), 200

        return jsonify(f'Organization with org_id {org_id} not found'), 404
    
    return jsonify("ERROR: request must be in JSON format"), 400

@app.route("/organization/search/<search_term>")
def get_organization_by_search(search_term, internal_call=False, p_auth_info=None):
    auth_info = {}
    if internal_call == False:
        auth_info = validate_auth_token(request.headers.get("auth_token"))
    elif p_auth_info:
        auth_info = p_auth_info
    
    if not auth_info:
        return jsonify("Access Denied"), 401
    
    search_term = search_term.lower()
    
    org_data = None
    if auth_info.user.role == 'admin' or auth_info.user.role == 'user':
        org_data = db.session.query(Organization)\
        .filter(db.func.lower(Organization.name).contains(search_term))\
        .filter(Organization.org_id == auth_info.user.org_id)\
        .order_by(Organization.name.asc())\
        .all()
    else:
        org_data = db.session.query(Organization)\
            .filter(db.func.lower(Organization.name).contains(search_term))\
            .order_by(Organization.name.asc())\
            .all()
    if (internal_call):
        return organizations_schema.dump(org_data)
    
    return jsonify(organizations_schema.dump(org_data))
    

@app.route("/search/<search_term>")
def get_objects_by_search(search_term):
    auth_info = validate_auth_token(request.headers.get("auth_token"))
    if not auth_info:
        return jsonify("Access Denied"), 401
    
    user_data = db.session.query(AppUser).filter(AppUser.user_id == auth_info.user.user_id).first()
    if auth_info.user.role in ['user', 'admin'] and (auth_info.user.org_id != user_data.org_id or auth_info.user.role != user_data.role):
        return jsonify("Unauthorized"), 403
    
    search_results = {}
    search_results["organizations"] = get_organization_by_search(search_term, True, auth_info)
    search_results["users"] = get_users_by_search(search_term, True, auth_info)
    return jsonify(search_results)

@app.route("/user/add", methods=["POST"])
def insert_user():
    if request.content_type == "application/json":
        auth_info = validate_auth_token(request.headers.get("auth_token"))
        if not auth_info or auth_info.user.role not in ['admin','super-admin']:
            return jsonify("Access Denied"), 401
            
        post_data = request.get_json()
        first_name = post_data.get('first_name')
        last_name = post_data.get('last_name')
        email = post_data.get('email')
        password = post_data.get('password')
        phone = post_data.get('phone')
        active = post_data.get('active')
        org_id = post_data.get('org_id')
        created_date = datetime.now()
        role = post_data.get('role')
        if (role == None or role not in ['super-admin', 'admin', 'user']):
            role = 'user'
        
        if auth_info.user.role != 'super-admin':
            if role == 'super-admin':
                role = 'user'
            org_id = auth_info.user.org_id
        
        organization = db.session.query(Organization).filter(Organization.org_id == org_id).first()
        if not organization:
            return jsonify(f"Unable to add User. Organization with id {org_id} not found"), 404
        if not organization.active:
            return jsonify(f"Unable to add User. Organization is inactive."), 403

        if active == None:
            active = True

        hashed_password = bcrypt.generate_password_hash(password).decode("utf8")
        stripped_phone = strip_phone(phone)
        record = AppUser(first_name, last_name, email, hashed_password, stripped_phone, created_date, org_id, role, active)

        db.session.add(record)
        db.session.commit()

        return jsonify("User created"), 201
    else:
        return jsonify("ERROR: request must be in JSON format"), 400

@app.route("/user/update", methods=["POST"])
def update_user():
    if request.content_type == "application/json":
        auth_info = validate_auth_token(request.headers.get("auth_token"))
        if not auth_info:
            return jsonify("Access Denied"), 401

        post_data = request.get_json()
        user_id = post_data.get("user_id")
        if user_id == None:
            return jsonify("ERROR: user_id missing"), 400
        org_id = post_data.get("org_id")
        first_name = post_data.get("first_name")
        last_name = post_data.get('last_name')
        email = post_data.get('email')
        password = post_data.get('password')
        phone = post_data.get('phone')
        role = post_data.get('role')
        active = post_data.get('active')
        if active == None:
            active = True
        
        user_data = None
        if auth_info.user.role == 'super-admin':
            user_data = db.session.query(AppUser).filter(AppUser.user_id == user_id).first()
        elif auth_info.user.role == 'admin':
            user_data = db.session.query(AppUser).filter(AppUser.user_id == user_id).filter(AppUser.org_id == auth_info.user.org_id).first()
        elif auth_info.user.role == 'user' and str(user_id) == str(auth_info.user.user_id):
            user_data = db.session.query(AppUser).filter(AppUser.user_id == auth_info.user.user_id).first()
        
        if user_data:
            user_data.user_id = user_id
            if org_id:
                user_data.org_id = org_id
            if first_name is not None:
                user_data.first_name = first_name
            if last_name is not None:
                user_data.last_name = last_name
            if email is not None:
                user_data.email = email
            if phone is not None:
                user_data.phone = strip_phone(phone)
            if role is not None:
                if auth_info.user.role == 'admin' and role != 'super-admin':
                    if role == 'user':
                        admins_in_org = db.session.query(AppUser).filter(AppUser.org_id == auth_info.user.org_id).all()
                        if not admins_in_org or len(admins_in_org) <= 1:
                            return jsonify("Cannot downgrade role of last admin in organization"), 403
                    user_data.role = role
                if auth_info.user.role == 'super-admin':
                    user_data.role = role
            if password is not None:
                user_data.password = bcrypt.generate_password_hash(password).decode("utf8")
            if active is not None:
                user_data.active = active

            db.session.commit()

            return jsonify(user_schema.dump(user_data)), 200
        else:
            return jsonify("User Not Found"), 404
    else:
        return jsonify("ERROR: request must be in JSON format"), 400
        
@app.route("/user/get", methods=["GET"])
def get_all_users():
    auth_info = validate_auth_token(request.headers.get("auth_token"))
    if not auth_info:
        return jsonify("Access Denied"), 401

    all_users = []

    if auth_info.user.role != 'super-admin':
        all_users = db.session.query(AppUser).filter(AppUser.org_id == auth_info.user.org_id).order_by(AppUser.last_name.asc()).order_by(AppUser.first_name.asc()).all()
    else:
        all_users = db.session.query(AppUser).order_by(AppUser.last_name.asc()).order_by(AppUser.first_name.asc()).all()
    
    return jsonify(users_schema.dump(all_users))

@app.route("/user/get/<user_id>", methods=["GET"])
def get_user_by_id(user_id):
    auth_info = validate_auth_token(request.headers.get("auth_token"))
    if not auth_info:
        return jsonify("Access Denied"), 401

    if validate_uuid4(user_id) == False:
        return jsonify("Invalid user ID"), 404

    user_data = {}
    
    if auth_info.user.role != 'super-admin':
        user_data = db.session.query(AppUser).filter(AppUser.user_id == user_id).filter(AppUser.org_id == auth_info.user.org_id).first()
    else:
        user_data = db.session.query(AppUser).filter(AppUser.user_id == user_id).first()
    if user_data:
        return jsonify(user_schema.dump(user_data))

    return jsonify(f'User with user_id {user_id} not found'), 404

@app.route("/user/get/me", methods=["GET"])
def get_user_from_auth_token():
    auth_info = validate_auth_token(request.headers.get("auth_token"))
    if not auth_info:
        return jsonify("Access Denied"), 401

    user_data = db.session.query(AppUser).filter(AppUser.user_id == auth_info.user_id).first()
    
    if user_data:
        return jsonify(user_schema.dump(user_data))

    return jsonify(f'User not found'), 404

@app.route("/user/get/organization/<org_id>", methods=["GET"])
def get_users_by_org_id(org_id):
    if request.content_type == "application/json":
        auth_info = validate_auth_token(request.headers.get("auth_token"))
        if not auth_info:
            return jsonify("Access Denied"), 401

        if validate_uuid4(org_id) == False:
            return jsonify("Invalid org ID"), 404

    users_by_org = db.session.query(AppUser).filter(AppUser.org_id == org_id).all()
    return jsonify(users_schema.dump(users_by_org))


@app.route("/user/delete/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    auth_info = validate_auth_token(request.headers.get("auth_token"))
    if not auth_info:
        return jsonify("Access Denied"), 401

    if validate_uuid4(user_id) == False:
        return jsonify("Invalid user ID"), 404
    
    if auth_info.user.user_id == user_id:
        return jsonify("Forbidden: User cannot delete themselves"), 403

    user_data = db.session.query(AppUser).filter(AppUser.user_id == user_id).first()
    if auth_info.user.role == 'user' or (auth_info.user.role == 'admin' and auth_info.user.org_id != user_data.org_id):
        return jsonify("Unauthorized"), 403
    
    if user_data:
        db.session.delete(user_data)
        db.session.commit()
        return jsonify(f'User with user_id {user_id} deleted'), 200

    
    return jsonify(f'User with user_id {user_id} not found'), 404

@app.route("/user/activate/<user_id>", methods=["PUT"])
def activate_user(user_id):
    if request.content_type == "application/json":
        auth_info = validate_auth_token(request.headers.get("auth_token"))
        if not auth_info:
            return jsonify("Access Denied"), 401

        if validate_uuid4(user_id) == False:
            return jsonify("Invalid user ID"), 404

        user_data = {}

        if auth_info.user.role == 'super-admin':
            user_data = db.session.query(AppUser).filter(AppUser.user_id == user_id).first()
        else:    
            user_data = db.session.query(AppUser).filter(AppUser.user_id == user_id).filter(AppUser.org_id == auth_info.user.org_id).first()
        
        if user_data:
            user_data.active = True
            db.session.commit()
            return jsonify(user_schema.dump(user_data))

        return jsonify(f'User with user_id {user_id} not found'), 404

    return("Request must be in JSON format"), 400

@app.route("/user/deactivate/<user_id>", methods=["PUT"])
def deactivate_user(user_id):
    if request.content_type == "application/json":
        auth_info = validate_auth_token(request.headers.get("auth_token"))
        if not auth_info:
            return jsonify("Access Denied"), 401

        if validate_uuid4(user_id) == False:
            return jsonify("Invalid user ID"), 404

        user_data = {}

        if auth_info.user.role == 'super-admin':
            user_data = db.session.query(AppUser).filter(AppUser.user_id == user_id).first()
        else:    
            user_data = db.session.query(AppUser).filter(AppUser.user_id == user_id).filter(AppUser.org_id == auth_info.user.org_id).first()
        
        if user_data:
            user_data.active = False
            db.session.commit()

            # Remove all auth records for anyone from that company
            auth_records = db.session.query(AuthToken).filter(AuthToken.user_id == user_id).all()
            
            for auth_record in auth_records:
                db.session.delete(auth_record)

            db.session.commit()


            return jsonify(user_schema.dump(user_data))

        return jsonify(f'User with user_id {user_id} not found'), 404
    
    return("Request must be in JSON format"), 400

@app.route("/user/search/<search_term>")
def get_users_by_search(search_term, internal_call=False, p_auth_info=None):
    auth_info = {}
    if internal_call == False:
        auth_info = validate_auth_token(request.headers.get("auth_token"))
    elif p_auth_info:
        auth_info = p_auth_info
    
    if not auth_info:
        return jsonify("Access Denied"), 401
    
    search_term = search_term.lower()
    
    user_data = {}

    if auth_info.user.role == 'admin' or auth_info.user.role == 'user':
        user_data = db.session.query(AppUser).join(Organization).filter(Organization.org_id == AppUser.org_id)\
            .filter(AppUser.org_id == auth_info.user.org_id) \
            .filter(db.or_( \
            db.func.lower(AppUser.first_name).contains(search_term), \
            db.func.lower(AppUser.last_name).contains(search_term), \
            AppUser.phone.contains(search_term), \
            db.func.lower(Organization.name).contains(search_term)
                )).order_by(AppUser.last_name.asc()).order_by(AppUser.first_name.asc()).all()
    else:
        user_data = db.session.query(AppUser).join(Organization).filter(Organization.org_id == AppUser.org_id)\
            .filter(db.or_( \
            db.func.lower(AppUser.first_name).contains(search_term), \
            db.func.lower(AppUser.last_name).contains(search_term), \
            AppUser.phone.contains(search_term), \
            db.func.lower(Organization.name).contains(search_term)
                )).order_by(AppUser.last_name.asc()).order_by(AppUser.first_name.asc()).all()
        
    if internal_call:
        return users_schema.dump(user_data)
    return jsonify(users_schema.dump(user_data))

@app.route("/user/auth", methods=["POST"])
def add_auth_token():
    if request.content_type == "application/json":
        post_data = request.get_json()
        email = post_data.get("email")
        password = post_data.get("password")
        if email == None:
            return jsonify("ERROR: email missing"), 400
        if password == None:
            return jsonify("ERROR: password missing"), 400

        expiration_datetime = datetime.utcnow() + timedelta(hours=12)
        user_data = db.session.query(AppUser)\
            .filter(AppUser.email == email)\
            .filter(AppUser.active).first()

        if user_data:
            if user_data.organization.active == False:
                return jsonify("Your account has been deactivated. Please contact your account executive."), 403

            is_password_valid = bcrypt.check_password_hash(user_data.password, password)
            if is_password_valid == False:
                return jsonify("Invalid email/password"), 401

            auth_data = db.session.query(AuthToken).filter(AuthToken.user_id == user_data.user_id).first()
            if auth_data == None:
                auth_data = AuthToken(user_data.user_id, expiration_datetime)
                db.session.add(auth_data)
            else:
                auth_data.expiration = expiration_datetime

        else: 
            return jsonify("Invalid email/password"), 401

        db.session.commit()

        return jsonify(auth_token_schema.dump(auth_data))
    else:
        return jsonify("ERROR: request must be made in JSON format"), 404

@app.route("/user/logout", methods=["PUT"])
def remove_auth_token():
    if request.content_type == "application/json":
        post_data = request.get_json()
        user_id = post_data.get("user_id")
        auth_token = post_data.get("auth_token")
        if (user_id == None or user_id == '') and (auth_token == None or auth_token == ''):
            return jsonify("Cannot log out a user with no user_id or auth_token"), 200
        # print("AUTH TOKEN: " + auth_token)
        if auth_token and auth_token != "not required":
            auth_data = db.session.query(AuthToken).filter(AuthToken.auth_token == auth_token).first()
        else:
            auth_data = db.session.query(AuthToken).filter(AuthToken.user_id == user_id).first()
        
        if auth_data:
            db.session.delete(auth_data)
            db.session.commit()
    
        return jsonify("User logged out"), 200
    else:
        return jsonify("ERROR: request must be in JSON format")

if __name__ == "__main__":
    app.run(debug=True)