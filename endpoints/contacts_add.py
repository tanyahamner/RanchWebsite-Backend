from flask import jsonify
import flask
from db import db
from models.contact_info import ContactInfo, contact_schema
from lib.authenticate import authenticate

@authenticate
def contact_add(req:flask.Request) -> flask.Response:
    post_data = req.get_json()
    user_id = post_data.get('user_id')
    contact_type = post_data.get('contact_type')
    contact_info = post_data.get('contact_info')
    

    check = db.session.query(ContactInfo).filter(ContactInfo.contact_type == contact_type).filter(ContactInfo.user_id == user_id).first
    if check != None:
        return jsonify("ERROR: Contact type already exists.")
    else:
        try:
            record = ContactInfo(user_id, contact_type, contact_info)
            db.session.add(record)
            db.session.commit()
        except: 
            return jsonify('ERROR: IDK')

    return jsonify("Contact Type Created"), 201
    