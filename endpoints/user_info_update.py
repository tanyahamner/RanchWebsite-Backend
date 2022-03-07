from flask import jsonify
import flask
from db import db
from models.contact_info import UserInfo, user_info_schema
from lib.authenticate import authenticate

@authenticate
def user_info_update(req:flask.Request) -> flask.Response:
    post_data = req.get_json()
    user_id = post_data.get('user_id')
    user_info_type = post_data.get('user_info_type')
    user_info = post_data.get('user_info')
    
    if user_id and user_info_type == None:
        return jsonify('ERROR: Primary Values missing')
    
    user_info_data = db.session.query(UserInfo).filter(UserInfo.user_id == user_id).first()

    if user_info_data:
        user_info_data.user_id = user_id
        if user_info_type:
            user_info_data.user_info_type = user_info_type
        if user_info:
            user_info_data.user_info = user_info

        db.session.commit

        return jsonify(user_info_schema.dump(user_info_data)), 200

    else:
        return jsonify('ERROR: Primary Values Not Found'), 404