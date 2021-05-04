from flask import jsonify
import flask
from db import db
from models.organizations import Organization, organizations_schema
from lib.authenticate import authenticate_return_auth

@authenticate_return_auth
def organizations_get(req:flask.Request, auth_info) -> flask.Response:
    all_organizations = []

    if auth_info.user.role != 'super-admin':
        all_organizations = db.session.query(Organization).filter(Organization.org_id == auth_info.user.org_id).order_by(Organization.name.asc()).all()
    else:
        all_organizations = db.session.query(Organization).order_by(Organization.name.asc()).all()
    
    return jsonify(organizations_schema.dump(all_organizations))