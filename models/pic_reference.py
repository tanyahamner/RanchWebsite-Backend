from flask_marshmallow import Marshmallow
from sqlalchemy.dialects.postgresql import UUID
import uuid
from db import db
import marshmallow as ma

class PicReference(db.Model):
    pic_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('app_user.user_id'), nullable=False)
    original_name = db.Column(db.String(), nullable = False)
    temp_name = db.Column(db.String(), nullable = False)
    file_size = db.Column(db.String(), nullable = False, unique = True)

    def __init__(self, user_id, original_name, temp_name, file_size):
        self.user_id = user_id
        self.original_name = original_name
        self.temp_name = temp_name
        self.file_size = file_size
   
class PicReferenceSchema(ma.Schema):
    class Meta:
        fields = ['pic_id', 'user_id', 'original_name', 'temp_name', 'file_size']
    
pic_schema = PicReferenceSchema()
pic_schema = PicReferenceSchema(many=True)