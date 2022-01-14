from flask_restful import Resource, reqparse, marshal_with, fields
from src.api.models import user_collection, UserModel, TokenModel
from src.utils.utils import get_response_format

auth_parser = reqparse.RequestParser()
auth_parser.add_argument("user_name", type=str, help="username is reuqired", required=True)
auth_parser.add_argument("pw", type=str, help="pw is reuqired", required=True)
auth_parser.add_argument("renew_token", type=bool)

mfields = get_response_format()

class AuthUser(Resource):
    def helper(self, user_name, pw, renew_token):
        result = user_collection.find_user_by_username(user_name)

        if result is None:
            return {"error" : "wrong user name"}, 401
        else:
            digest = result['token']['digest']
            
            if UserModel.hash_pw(pw) == result['hashed_pw']:
                if renew_token:
                    updated_res = user_collection.renew_token(user_name)
                    digest = updated_res['token']['digest']

                return {"message" : "user authenticated", "payload": {"bearer_token" : digest, "user_name":user_name}}
            return {"error" : "wrong password"}, 401

    @marshal_with(mfields)
    def patch(self):
        args = auth_parser.parse_args()
        user_name, pw, renew_token = args['user_name'], args['pw'], args['renew_token']
        if not renew_token:
            return {"message":"method not allowed"}, 405
        return self.helper(user_name, pw, renew_token)
    
    @marshal_with(mfields)  
    def get(self):
        args = auth_parser.parse_args()
        user_name, pw, renew_token = args['user_name'], args['pw'], args['renew_token']
        if renew_token:
            return {"message":"method not allowed"}, 405
        return self.helper(user_name, pw, False)

    
    @marshal_with(mfields)
    def post(self):
        args = auth_parser.parse_args()
        user_name, pw = args['user_name'], args['pw']

        result = user_collection.find_user_by_username(user_name)
        if result is None:
            token = TokenModel(user_name)
            new_user = UserModel(user_name, pw, token)

            inserted_id = user_collection.insert_user(new_user)
            if (inserted_id):
                return {"message" : "user created", "payload" : {"bearer_token" : token.digest, 'user_name':user_name}}

            return {"error" : "internal error happened, please try again"}, 500
        return {"error" : "username already existed"}, 401
    
