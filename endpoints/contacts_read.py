from flask import jsonify
import flask
from db import db
from models.app_users import AppUsers
from models.contact_info import ContactInfo, contact_schema
from lib.authenticate import authenticate_return_auth

@authenticate_return_auth
def read_contact(req:flask.Request, user_id=None, auth_info=None) -> flask.Response:
    
    contacts = db.session.query(ContactInfo).filter(ContactInfo.user_id == user_id).first()
    if contacts == None or []:
        return jsonify("No data for user.")
    return contact_schema.dump(contacts)
    