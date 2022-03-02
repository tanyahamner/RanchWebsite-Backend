from flask import jsonify
import flask
from db import db
from models.app_users import AppUsers, users_schema
from lib.authenticate import authenticate_return_auth

@authenticate_return_auth
def users_get_all(req:flask.Request, auth_info) -> flask.Response:
    all_users = []

    if auth_info.user.role != 'super-admin':
        all_users = db.session.query(AppUsers).filter(AppUsers.org_id == auth_info.user.org_id).order_by(AppUsers.last_name.asc()).order_by(AppUsers.first_name.asc()).all()
    else:
        all_users = db.session.query(AppUsers).order_by(AppUsers.last_name.asc()).order_by(AppUsers.first_name.asc()).all()
    
    return jsonify(users_schema.dump(all_users))