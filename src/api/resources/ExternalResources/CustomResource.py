from flask_restful import marshal_with
from flask import request, session
import requests
from .Base import BaseResource

from src.utils.utils import get_response_format


mfields = get_response_format()

class CustomResource(BaseResource):
    REMOTE_RESOURCE_PATH = 'custom_resource'

    @marshal_with(mfields)
    def post(self):
        # resource name is repo name received from user
        user_name, resource_name = request.get_json()['user_name'], request.get_json()['resource_name']

        if not (user_name and resource_name):
            return {"error" : "Missing username & resource name"}

        if resource_name in session:
            return {"payload" : session[resource_name]}

        r = requests.post(f"{self.EXT_SERVICE}/{self.REMOTE_RESOURCE_PATH}", data={"user_name" : user_name, "resource_name" : resource_name})
        json_res = r.json()

        print(json_res)
        
        address = json_res['payload']
        session[resource_name] = address
        return {"payload" : address, "error" : json_res['error']}
    
    @marshal_with(mfields)
    def delete(self):
        user_name, resource_name = request.get_json()['user_name'], request.get_json()['resource_name']

        if not (user_name and resource_name):
            return {"error" : "Missing username & resource name"}

        r = requests.delete(f"{self.EXT_SERVICE}/{self.REMOTE_RESOURCE_PATH}", data={"user_name" : user_name, "resource_name" : resource_name})
        json_res = r.json()

        try:
            session.pop(resource_name)
        except:
            pass

        return {"message" : json_res['message']}