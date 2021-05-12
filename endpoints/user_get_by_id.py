from flask import jsonify
import flask
from db import db
from models.app_users import AppUser, user_schema
from lib.authenticate import authenticate_return_auth
from util.validate_uuid4 import validate_uuid4

@authenticate_return_auth
def user_get_by_id(req:flask.Request, user_id, auth_info) -> flask.Response:
    user_id = user_id.strip()
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