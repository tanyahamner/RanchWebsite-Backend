from flask import jsonify
import flask
from db import db
from models.organizations import Organization, organization_schema
from lib.authenticate import authenticate_return_auth
from util.validate_uuid4 import validate_uuid4

@authenticate_return_auth
def organization_activate_by_id(req:flask.Request, org_id, auth_info) -> flask.Response:
    org_id = org_id.strip()
    if validate_uuid4(org_id) == False:
            return jsonify("Invalid org ID"), 404

    org_data = db.session.query(Organization).filter(Organization.org_id == org_id).first()
    if org_data:
        org_data.active = True
        db.session.commit()
        return jsonify(organization_schema.dump(org_data)), 200

        return jsonify(f'Organization with org_id {org_id} not found'), 404
    
    return jsonify("ERROR: request must be in JSON format"), 400