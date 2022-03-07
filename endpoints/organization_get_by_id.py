from flask import jsonify
import flask
from db import db
from models.organizations import Organizations, organizations_schema
from lib.authenticate import authenticate_return_auth
from util.validate_uuid4 import validate_uuid4

@authenticate_return_auth
def organization_get_by_id(req:flask.Request, org_id, auth_info) -> flask.Response:
    org_id = org_id.strip()
    if validate_uuid4(org_id) == False:
        return jsonify("Invalid org ID"), 404
    org_query = db.session.query(Organizations).filter(Organizations.org_id == org_id)

    if auth_info.user.role != 'super-admin':
        org_query = org_query.filter(Organizations.org_id == auth_info.user.org_id)
    
    org_data = org_query.first()

    if org_data:
        return jsonify(organizations_schema.dump(org_data))

    return jsonify(f"Organizations with org_id {org_id} not found"), 404