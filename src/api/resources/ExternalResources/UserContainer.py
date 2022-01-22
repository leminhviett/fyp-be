from urllib import request
from flask_restful import Resource, reqparse, marshal_with, fields
from src.api.middlewares.protector import protected_by_token
from src.api.models import user_collection, UserModel, TokenModel
from src.utils.utils import get_response_format
from flask import request

from src.api.resources.AuthUser import AuthUser
import requests

mfields = get_response_format()

class UserContainer(Resource):
    EXT_SERVICE = "http://localhost:8000"

    @marshal_with(mfields)
    def post(self):
        user_name, pw = request.get_json()['user_name'], request.get_json()['pw']
        auth_res = AuthUser.helper(user_name, pw, False)

        if "error" in auth_res:
            return auth_res
        # return {"message" : "user container"}
        r = requests.post(f"{UserContainer.EXT_SERVICE}/kali_container", data={"user_name" : user_name, "pw" : pw})
        json_res = r.json()
        return {"payload" : json_res}

        return {'payload' : {'topics' : result['topics'], 'challenges': result['challenges']}}

