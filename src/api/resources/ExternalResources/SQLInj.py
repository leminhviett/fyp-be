from audioop import add
from flask_restful import Resource, marshal_with
from flask import request, session
import requests

from src.utils.utils import get_response_format


mfields = get_response_format()

class SQLInj(Resource):
    EXT_SERVICE = "http://localhost:8000"

    @marshal_with(mfields)
    def post(self):
        user_name = request.get_json()['user_name']

        if 'sql_inj' in session:
            return {"payload" : session['sql_inj']}

        r = requests.post(f"{SQLInj.EXT_SERVICE}/sql_inj", data={"user_name" : user_name})
        json_res = r.json()
        print(json_res)
        address = json_res['payload']
        session['sql_inj'] = address
        return {"payload" : address}
    
    @marshal_with(mfields)
    def delete(self):
        user_name = request.get_json()['user_name']

        r = requests.delete(f"{SQLInj.EXT_SERVICE}/sql_inj", data={"user_name" : user_name})
        json_res = r.json()

        try:
            session.pop('sql_inj')
        except:
            pass

        return {"message" : json_res['message']}