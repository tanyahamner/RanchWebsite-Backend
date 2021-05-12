from flask import jsonify
import flask
from db import db
from models.app_users import AppUser, user_schema
from models.auth_tokens import AuthToken, auth_token_schema
from lib.authenticate import authenticate_return_auth
from util.validate_uuid4 import validate_uuid4

@authenticate_return_auth
def user_deactivate(req:flask.Request, user_id, auth_info) -> flask.Response:
    if validate_uuid4(user_id) == False:
        return jsonify("Invalid user ID"), 404

    user_data = {}
    if str(user_id) == str(auth_info.user.user_id):
        return jsonify('ERROR: cannot deactivate your own user'), 405
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