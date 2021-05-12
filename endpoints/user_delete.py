from flask import jsonify
import flask
from db import db
from models.app_users import AppUser, user_schema
from lib.authenticate import authenticate_return_auth
from util.validate_uuid4 import validate_uuid4

@authenticate_return_auth
def user_delete(req:flask.Request, auth_info) -> flask.Response:
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