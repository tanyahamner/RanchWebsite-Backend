from flask import jsonify
import flask
from db import db
from models.contact_info import UserInfo
from lib.authenticate import authenticate

@authenticate
def user_info_add(req:flask.Request) -> flask.Response:
    post_data = req.get_json()
    user_id = post_data.get('user_id')
    user_info_type = post_data.get('user_info_type')
    user_info = post_data.get('user_info_')
    

    check = db.session.query(UserInfo).filter(UserInfo.user_info_type == user_info_type).filter(UserInfo.user_id == user_id).first
    if check != None:
        return jsonify("ERROR: UserInfo type already exists.")
    else:
        try:
            record = UserInfo(user_id, user_info_type, user_info)
            db.session.add(record)
            db.session.commit()
        except: 
            return jsonify('ERROR: IDK')

    return jsonify("Contact Type Created"), 201
    