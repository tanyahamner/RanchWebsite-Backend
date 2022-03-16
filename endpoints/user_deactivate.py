from flask import jsonify
import flask
from db import db
from models.app_users import AppUsers, user_schema
from models.auth_tokens import AuthTokens, auth_token_schema
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
        user_data = db.session.query(AppUsers).filter(AppUsers.user_id == user_id).first()
    else:    
        user_data = db.session.query(AppUsers).filter(AppUsers.user_id == user_id).filter(AppUsers.org_id == auth_info.user.org_id).first()
    
    if user_data:
        user_data.active = False
        db.session.commit()

        auth_records = db.session.query(AuthTokens).filter(AuthTokens.user_id == user_id).all()
        
        for auth_record in auth_records:
            db.session.delete(auth_record)

        db.session.commit()


        return jsonify(user_schema.dump(user_data))

    
    return("Request must be in JSON format"), 400