from flask import jsonify
import flask
import os, sys
from db import db
from models.app_users import AppUser, user_schema
from PIL import Image
import io
from lib.authenticate import authenticate_return_auth

@authenticate_return_auth
def pic_add(req:flask.Request, auth_info) -> flask.Response:
    post_data = req.get_json()
    file_bytes = post_data.get('pic_bytes')

    path = os.getcwd() + "/endpoints/uploads/images"
    
    with open(path, "ab") as output:
        output.write(file_bytes)

    return