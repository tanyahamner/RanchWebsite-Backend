from flask_marshmallow import Marshmallow
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from db import db
import marshmallow as ma
from models.app_users import AppUsers

class UserInfo(db.Model):
    __tablename__= 'ContactInfo'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('AppUsers.user_id', ondelete='CASCADE'))
    user_info_type = db.Column(db.String())
    user_info_info = db.Column(db.String())

    def __init__(self, user_id, user_info_type, user_info):
        self.user_id = user_id
        self.user_info_type = user_info_type
        self.user_info_info = user_info

class UserInfoSchema(ma.Schema):
    class Meta:
        fields = ['user_id','user_info_type','user_info']
    
user_info_schema = UserInfoSchema()
users_info_schema = UserInfoSchema(many=True)