from flask import jsonify
import flask
from db import db
from models.contact_info import ContactInfo, contact_schema
from lib.authenticate import authenticate
from util.validate_uuid4 import validate_uuid4

@authenticate
def contacts_delete(req:flask.Request, user_id, contact_type) -> flask.Response:
    if validate_uuid4(user_id)== False:
        return jsonify("Invalid user ID"),404
    
    contacts = db.session.query(ContactInfo).filter(ContactInfo.user_id == user_id)
    contact_removal = []
    for info in contacts:
        if info[1] == contact_type:
            contact_removal.append[info]
        else:
            continue
        if contact_removal != []:
            for item in contact_removal:
                db.session.delete(item)
            db.session.commit()
            return jsonify(f'{contact_type} for {user_id} deleted')
        
        return jsonify(f'{contact_type} not found for{user_id}')
