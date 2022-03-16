from flask import jsonify
import flask
from db import db
from models.organizations import Organizations, organizations_schema
from models.app_users import AppUsers, users_schema
from models.activate_email_tokens import ActivateEmailTokens
from lib.authenticate import authenticate_return_auth
from datetime import datetime
from util.validate_uuid4 import validate_uuid4
from util.foundation_utils import strip_phone


@authenticate_return_auth
def user_add(req:flask.Request, bcrypt, auth_info) -> flask.Response:
    post_data = req.get_json()
    first_name = post_data.get('first_name')
    last_name = post_data.get('last_name')
    email = post_data.get('email')
    password = post_data.get('password')
    active = post_data.get('active')
    org_id = post_data.get('org_id')
    created_date = datetime.now()
    role = post_data.get('role')
    if (role == None or role in ['super-admin', 'admin', 'user']):
        role = 'user'
        
        if auth_info.user.role != 'super-admin':
            if role == 'super-admin':
                role = 'user'
            org_id = auth_info.user.org_id
        
        Organizations = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
        if not Organizations:
            return jsonify(f"Unable to add User. Organizations with id {org_id} not found"), 404
        if not Organizations.active:
            return jsonify(f"Unable to add User. Organizations is inactive."), 403

        hashed_password = bcrypt.generate_password_hash(password).decode("utf8")
    
        record = AppUsers(first_name, last_name, email, hashed_password, created_date, org_id, role, active)
        

        db.session.add(record)
        db.session.commit()

        user_id = (db.session.query(AppUsers).filter(AppUsers.email == email).fetchone())[0]

        record = ActivateEmailTokens(user_id)

        db.session.add(record)
        db.session.commit()
        
        return jsonify("User created"), 201
    else:
        return jsonify("ERROR: user role not in list"), 400