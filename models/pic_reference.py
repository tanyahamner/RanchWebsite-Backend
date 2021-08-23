from flask_marshmallow import Marshmallow
from sqlalchemy.dialects.postgresql import UUID
import uuid
from db import db
import marshmallow as ma

class PicReference(db.Model):
    pic_id = db.Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('app_user.user_id'), nullable=False)
    original_name = db.Column(db.String(), nullable = False)
    ext = db.Column(db.String(), nullable = False)

    def __init__(self, pic_id, user_id, original_name, ext):
        self.pic_id = pic_id
        self.user_id = user_id
        self.original_name = original_name
        self.ext = ext
   
class PicReferenceSchema(ma.Schema):
    class Meta:
        fields = ['pic_id', 'user_id', 'original_name', 'ext']
    
pic_schema = PicReferenceSchema()
pics_schema = PicReferenceSchema(many=True)