from flask import jsonify
import flask
from db import db
from models.auth_tokens import AuthTokens, auth_token_schema
from lib.authenticate import authenticate_return_auth
from util.validate_uuid4 import validate_uuid4

def auth_token_remove(req:flask.Request) -> flask.Response:
    if req.content_type == "application/json":
        post_data = req.get_json()
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