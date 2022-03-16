from flask import jsonify
import flask
from db import db
from models.contact_info import ContactInfo, contact_info_schema
from lib.authenticate import authenticate

@authenticate
def contact_update(req:flask.Request) -> flask.Response:
    post_data = req.get_json()
    user_id = post_data.get('user_id')
    contact_type = post_data.get('contact_value')
    contact_value = post_data.get('contact_value')
    
    if user_id and contact_value == None:
        return jsonify('ERROR: Primary Values missing')
    
    contact_data = db.session.query(UserInfo).filter(UserInfo.user_id == user_id).first()

    if contact_data:
        contact_data.user_id = user_id
        if contact_value:
            contact_data.contact_value = contact_value
        if contact_type:
            contact_data.contact_type = contact_type

        db.session.commit

        return jsonify(contact_info_schema.dump(contact_data)), 200

    else:
        return jsonify('ERROR: Primary Values Not Found'), 404