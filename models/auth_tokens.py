from flask_marshmallow import Marshmallow
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from db import db
import marshmallow as ma
from .app_users import AppUserSchema

class AuthToken(db.Model):
    auth_token = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('app_user.user_id'), nullable=False)
    expiration = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, expiration):
        self.user_id = user_id
        self.expiration = expiration

class AuthTokenSchema(ma.Schema):
    class Meta:
        fields = ['auth_token', 'user', 'expiration']
    user = ma.fields.Nested(AppUserSchema(only=("role", "first_name", "user_id", "org_id")))

auth_token_schema = AuthTokenSchema()

