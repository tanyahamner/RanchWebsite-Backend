from flask import jsonify
import flask
from db import db
from models.organizations import Organizations, organizations_schema
from lib.authenticate import authenticate
from util.foundation_utils import strip_phone

@authenticate
def organization_update(req:flask.Request) -> flask.Response:
    post_data = req.get_json()
    org_id = post_data.get("org_id")
    if org_id == None:
        return jsonify("ERROR: org_id missing"), 400
    name = post_data.get('name')
    address = post_data.get('address')
    city = post_data.get('city')
    state = post_data.get('state')
    zip_code = post_data.get('zip_code')
    phone = post_data.get('phone')
    active = post_data.get('active')
    if active == None:
        active = True

    org_data = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
    org_data.name = name
    org_data.address = address
    org_data.city = city
    org_data.state = state
    org_data.zip_code = zip_code
    org_data.phone = strip_phone(phone)
    org_data.active = active

    db.session.commit()

    return jsonify(organizations_schema.dump(org_data)), 200