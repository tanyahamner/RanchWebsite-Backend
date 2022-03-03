from flask import jsonify
import flask
from db import db
from models.contact_info import ContactInfo, contact_schema
from lib.authenticate import authenticate

@authenticate
def contacts_update(req:flask.Request) -> flask.Response:
    post_data = req.get_json()
    user_id = post_data.get('user_id')
    contact_type = post_data.get('contact_type')
    contact_info = post_data.get('contact_info')
    
    if user_id and contact_type == None:
        return jsonify('ERROR: Primary Values missing')
    
    contact_data = db.session.query(ContactInfo).filter(ContactInfo.user_id == user_id).first()

    if contact_data:
        contact_data.user_id = user_id
        if contact_type:
            contact_data.contact_type = contact_type
        if contact_info:
            contact_data.contact_info = contact_info

        db.session.commit

        return jsonify(contact_schema.dump(contact_data)), 200

    else:
        return jsonify('ERROR: Primary Values Not Found'), 404