from flask import jsonify
import flask
from db import db
from models.app_users import AppUsers, user_schema
from lib.authenticate import authenticate_return_auth
from util.foundation_utils import strip_phone
from util.validate_uuid4 import validate_uuid4

@authenticate_return_auth
def user_update(req:flask.Request, auth_info) -> flask.Response:
    post_data = req.get_json()
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
            user_data = db.session.query(AppUsers).filter(AppUsers.user_id == user_id).first()
        elif auth_info.user.role == 'admin':
            user_data = db.session.query(AppUsers).filter(AppUsers.user_id == user_id).filter(AppUsers.org_id == auth_info.user.org_id).first()
        elif auth_info.user.role == 'user' and str(user_id) == str(auth_info.user.user_id):
            user_data = db.session.query(AppUsers).filter(AppUsers.user_id == auth_info.user.user_id).first()
        
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
                        admins_in_org = db.session.query(AppUsers).filter(AppUsers.org_id == auth_info.user.org_id).all()
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