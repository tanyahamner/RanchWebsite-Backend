from flask import jsonify
import flask
from db import db
from models.organizations import Organizations, organizations_schema
from models.auth_tokens import AuthTokens, auth_token_schema

from lib.authenticate import authenticate_return_auth
from util.validate_uuid4 import validate_uuid4

@authenticate_return_auth
def organization_deactivate_by_id(req:flask.Request, org_id, auth_info) -> flask.Response:
    org_id = org_id.strip()
    if validate_uuid4(org_id) == False:
        return jsonify("Invalid org ID"), 404

    if org_id == auth_info.user.org_id:
        return jsonify("Access Denied: You cannot delete your own Organizations"), 401

    org_data = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
    if org_data:
        org_data.active = False
        db.session.commit()

        return jsonify(organizations_schema.dump(org_data)), 200

