from flask import jsonify
import flask
from db import db
from models.organizations import Organizations, organizations_schema
from lib.authenticate import authenticate_return_auth

@authenticate_return_auth
def organizations_get(req:flask.Request, auth_info) -> flask.Response:
    all_Organizations = []

    if auth_info.user.role != 'super-admin':
        all_Organizations = db.session.query(Organizations).filter(Organizations.org_id == auth_info.user.org_id).order_by(Organizations.name.asc()).all()
    else:
        all_Organizations = db.session.query(Organizations).order_by(Organizations.name.asc()).all()
    
    return jsonify(organizations_schema.dump(all_Organizations))