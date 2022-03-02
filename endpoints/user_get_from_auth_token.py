from flask import jsonify
import flask
from db import db
from models.app_users import AppUsers, user_schema
from lib.authenticate import authenticate_return_auth

@authenticate_return_auth
def user_get_from_auth_token(req:flask.Request, auth_info) -> flask.Response:
    user_data = db.session.query(AppUsers).filter(AppUsers.user_id == auth_info.user_id).first()
    
    if user_data:
        return jsonify(user_schema.dump(user_data))

    return jsonify(f'User not found'), 404