from flask import jsonify
import flask
from db import db
from models.app_users import AppUser, user_schema
from lib.authenticate import authenticate_return_auth
from util.validate_uuid4 import validate_uuid4

@authenticate_return_auth
def users_get_by_org_id(req:flask.Request, org_id, auth_info) -> flask.Response:
    if validate_uuid4(org_id) == False:
        return jsonify("Invalid org ID"), 404

    users_by_org = db.session.query(AppUser).filter(AppUser.org_id == org_id).all()
    return jsonify(user_schema.dump(users_by_org))