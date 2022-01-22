from datetime import datetime
import functools, jwt, os
import re
from flask import request
from src.api.models import *
from datetime import datetime

def protected_by_token(func):
    @functools.wraps(func)
    def wrapper(*args, **kargs):
        try:
            bearer_token = request.get_json()['bearer_token']
        except:
            try:
                bearer_token = request.form['bearer_token']
            except:
                try:
                    bearer_token = request.headers.get('bearer_token')
                except:
                    return {"error" : "Token is missing"}, 401

        # print(request.headers)
        # print("json :", request.get_json())

        # print(bearer_token)
        print("header: ", bearer_token)
        if bearer_token is None:
            print('token is none')
            return {"error" : "Token is missing"}, 401

        try:
            data = jwt.decode(bearer_token, os.getenv("SECRET_KEY"),algorithms=["HS256"])
            exp = data['exp']
            if not TokenModel.valid(exp):
                return {"error" : "Token expired"}, 401
            
            return func(*args, **kargs, user_name=data['user_name'])
        except Exception as e:
            print(e)
            return {"error" : e}, 401

    return wrapper