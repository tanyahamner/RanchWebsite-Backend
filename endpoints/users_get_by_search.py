from flask import jsonify
import flask
from db import db
from models.organizations import Organizations, organizations_schema
from models.app_users import AppUsers, users_schema
from lib.authenticate import authenticate_return_auth
from util.validate_uuid4 import validate_uuid4

@authenticate_return_auth
def users_get_by_search(req:flask.Request, search_term, internal_call, p_auth_info, auth_info) -> flask.Response:
    search_term = search_term.lower()
    
    user_data = {}

    if auth_info.user.role == 'admin' or auth_info.user.role == 'user':
        user_data = db.session.query(AppUsers).join(Organizations).filter(Organizations.org_id == AppUsers.org_id)\
            .filter(AppUsers.org_id == auth_info.user.org_id) \
            .filter(db.or_( \
            db.func.lower(AppUsers.first_name).contains(search_term), \
            db.func.lower(AppUsers.last_name).contains(search_term), \
            AppUsers.phone.contains(search_term), \
            db.func.lower(Organizations.name).contains(search_term)
                )).order_by(AppUsers.last_name.asc()).order_by(AppUsers.first_name.asc()).all()
    else:
        user_data = db.session.query(AppUsers).join(Organizations).filter(Organizations.org_id == AppUsers.org_id)\
            .filter(db.or_( \
            db.func.lower(AppUsers.first_name).contains(search_term), \
            db.func.lower(AppUsers.last_name).contains(search_term), \
            AppUsers.phone.contains(search_term), \
            db.func.lower(Organizations.name).contains(search_term)
                )).order_by(AppUsers.last_name.asc()).order_by(AppUsers.first_name.asc()).all()
        
    if internal_call:
        return users_schema.dump(user_data)
    return jsonify(users_schema.dump(user_data))