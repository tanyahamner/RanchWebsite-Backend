from flask import jsonify
import flask
from db import db
from models.organizations import Organizations, organizations_schema
from models.app_users import AppUsers, user_schema
from models.auth_tokens import AuthTokens, auth_token_schema
from lib.authenticate import authenticate_return_auth
from datetime import datetime, timedelta
from util.validate_uuid4 import validate_uuid4

def auth_token_add(req:flask.Request, bcrypt) -> flask.Response:
    if req.content_type == "application/json":
        post_data = req.get_json()
        email = post_data.get("email")
        password = post_data.get("password")
        if email == None:
            return jsonify("ERROR: email missing"), 400
        if password == None:
            return jsonify("ERROR: password missing"), 400

        now_datetime = datetime.utcnow()
        expiration_datetime = datetime.utcnow() + timedelta(hours=12)
        user_data = db.session.query(AppUsers)\
            .filter(AppUsers.email == email)\
            .filter(AppUsers.active).first()

        if user_data:
            if user_data.Organizations.active == False:
                return jsonify("Your account has been deactivated. Please contact your account executive."), 403

            is_password_valid = bcrypt.check_password_hash(user_data.password, password)
            if is_password_valid == False:
                return jsonify("Invalid email/password"), 401

            auth_data = db.session.query(AuthTokens).filter(AuthTokens.user_id == user_data.user_id).first()
            if auth_data is None:
                auth_data = AuthTokens(user_data.user_id, expiration_datetime)
                db.session.add(auth_data)
            else:
                # auth_record = db.session.query(AuthToken).filter(AuthToken.auth_token == auth_token).filter(AuthToken.expiration > datetime.utcnow()).first()
                print(auth_data.expiration)
                # 2021-05-11 05:11:13.899410
                # old_expiration_datetime = datetime.strptime(auth_data.expiration, '%Y-%m-%d %H:%M:%S.%f')
                if now_datetime < auth_data.expiration:
                    # Auth Expired
                    db.session.delete(auth_data)
                    auth_data = AuthTokens(user_data.user_id, expiration_datetime)
                    db.session.add(auth_data)
                else:
                    auth_data.expiration = expiration_datetime
        else: 
            return jsonify("Invalid email/password"), 401

        db.session.commit()

        return jsonify(auth_token_schema.dump(auth_data))
    else:
        return jsonify("ERROR: request must be made in JSON format"), 404