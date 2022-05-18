from flask import jsonify
import flask
from db import db
<<<<<<< HEAD:controllers/search_controller.py
from models.app_users import AppUser
=======
from models.organizations import Organizations, organizations_schema
from models.app_users import AppUsers, user_schema
>>>>>>> dev:endpoints/get_objects_by_search.py
from lib.authenticate import authenticate_return_auth
import controllers

@authenticate_return_auth
def get_objects_by_search(req:flask.Request, search_term, auth_info) -> flask.Response:
    user_data = db.session.query(AppUsers).filter(AppUsers.user_id == auth_info.user.user_id).first()
    if auth_info.user.role in ['user', 'admin'] and (auth_info.user.org_id != user_data.org_id or auth_info.user.role != user_data.role):
        return jsonify("Unauthorized"), 403
    
    search_results = {}
<<<<<<< HEAD:controllers/search_controller.py
    search_results["organizations"] = controllers.organization_get_by_search(req, search_term, True, auth_info)
    search_results["users"] = controllers.users_get_by_search(req, search_term, True, auth_info)
=======
    search_results["Organizationss"] = endpoints.Organizations_get_by_search(req, search_term, True, auth_info)
    search_results["users"] = endpoints.users_get_by_search(req, search_term, True, auth_info)
>>>>>>> dev:endpoints/get_objects_by_search.py
    return jsonify(search_results)