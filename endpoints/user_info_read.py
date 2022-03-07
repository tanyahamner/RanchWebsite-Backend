from flask import jsonify
import flask
from db import db
from models.app_users import AppUsers
from models.contact_info import UserInfo, user_info_schema
from lib.authenticate import authenticate_return_auth

@authenticate_return_auth
def read_user_info(req:flask.Request, user_id=None, auth_info=None) -> flask.Response:
    
    contacts = db.session.query(UserInfo).filter(UserInfo.user_id == user_id).first()
    if contacts == None or []:
        return jsonify("No data for user.")
    return user_info_schema.dump(contacts)
    