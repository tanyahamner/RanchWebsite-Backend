from flask import jsonify
import flask
from db import db
from models.contact_info import UserInfo, user_info_schema
from lib.authenticate import authenticate
from util.validate_uuid4 import validate_uuid4

@authenticate
def user_info_delete(req:flask.Request, user_id, user_info_type) -> flask.Response:
    if validate_uuid4(user_id)== False:
        return jsonify("Invalid user ID"),404
    
    user_info = db.session.query(UserInfo).filter(UserInfo.user_id == user_id)
    user_info_removal = []
    for info in user_info:
        if info[1] == user_info_type:
            user_info_removal.append[info]
        else:
            continue
        if user_info_removal != []:
            for item in user_info_removal:
                db.session.delete(item)
            db.session.commit()
            return jsonify(f'{user_info_type} for {user_id} deleted')
        
        return jsonify(f'{user_info_type} not found for{user_id}')
