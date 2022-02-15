from flask_restful import marshal_with
from flask import request, session
import requests

from src.api.resources.AuthUser import AuthUser
from src.utils.utils import get_response_format
from .Base import BaseResource


mfields = get_response_format()

class UserContainer(BaseResource):

    @marshal_with(mfields)
    def post(self):
        user_name, pw = request.get_json()['user_name'], request.get_json()['pw']

        if not (user_name and pw):
            return {"error" : "Missing username & pw"}

        if 'personal_VM' in session:
            return {"payload" :session['personal_VM']}

        auth_res = AuthUser.helper(user_name, pw, False)
        if "error" in auth_res:
            return auth_res

        r = requests.post(f"{self.EXT_SERVICE}/kali_container", data={"user_name" : user_name, "pw" : pw})
        json_res = r.json()

        address = json_res['payload']

        session['personal_VM'] = address
        return {"payload" : address}
    
    @marshal_with(mfields)
    def delete(self):
        user_name, pw = request.get_json()['user_name'], request.get_json()['pw']

        if not (user_name and pw):
            return {"error" : "Missing username & pw"}

        auth_res = AuthUser.helper(user_name, pw, False)
        if "error" in auth_res:
            return auth_res

        r = requests.delete(f"{self.EXT_SERVICE}/kali_container", data={"user_name" : user_name})
        json_res = r.json()

        try:
            session.pop('personal_VM')
        except:
            pass

        return {"message" : json_res['message']}

