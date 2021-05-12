from flask import jsonify
import flask
from db import db
from models.app_users import AppUser, users_schema
from lib.authenticate import authenticate_return_auth

@authenticate_return_auth
def users_get_all(req:flask.Request, auth_info) -> flask.Response:
    all_users = []

    if auth_info.user.role != 'super-admin':
        all_users = db.session.query(AppUser).filter(AppUser.org_id == auth_info.user.org_id).order_by(AppUser.last_name.asc()).order_by(AppUser.first_name.asc()).all()
    else:
        all_users = db.session.query(AppUser).order_by(AppUser.last_name.asc()).order_by(AppUser.first_name.asc()).all()
    
    return jsonify(users_schema.dump(all_users))