from flask_marshmallow import Marshmallow
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from db import db
import marshmallow as ma

class Organization(db.Model):
    org_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(), nullable = False, unique = True)
    address = db.Column(db.String())
    city = db.Column(db.String())
    state = db.Column(db.String())
    zip_code = db.Column(db.String())
    phone = db.Column(db.String())
    active = db.Column(db.Boolean(), nullable=False, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('AppUser', cascade="all,delete", backref = 'organization')
    
    def __init__(self, name, address, city, state, zip_code, phone, created_date, active = True):
        self.name = name
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.phone = phone
        self.created_date = created_date
        self.active = active
   
   
class OrganizationSchema(ma.Schema):
    class Meta:
        fields = ['org_id','name', 'address', 'city', 'state', 'zip_code', 'phone', 'created_date', 'active']

organization_schema = OrganizationSchema()
organizations_schema = OrganizationSchema(many=True)
