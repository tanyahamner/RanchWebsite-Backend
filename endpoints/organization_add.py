from flask import jsonify
import flask
from db import db
from models.organizations import Organization, organization_schema
from lib.authenticate import authenticate
from util.foundation_utils import strip_phone
from datetime import datetime

@authenticate
def organization_add(req:flask.Request) -> flask.Response:
    post_data = req.get_json()
    name = post_data.get('name')
    address = post_data.get('address')
    city = post_data.get('city')
    state = post_data.get('state')
    zip_code = post_data.get('zip_code')
    phone = post_data.get('phone')
    active = post_data.get('active')
    created_date = datetime.now()
    if active == None:
        active = True

    stripped_phone = strip_phone(phone)
    org_data = Organization(name, address, city, state, zip_code, stripped_phone, created_date, active)

    db.session.add(org_data)
    db.session.commit()

    return jsonify(organization_schema.dump(org_data)), 201