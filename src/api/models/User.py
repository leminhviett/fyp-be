from pymongo.database import Database
import hashlib, jwt, os
from src.api.models import TokenModel, db_err_handler

class UserModel:
    def __init__(self, user_name, pw, token:TokenModel,topics=[], challenges=[]):
       self.user_name = user_name
       self.hashed_pw = self.hash_pw(pw)
       self.topics = topics
       self.challenges = challenges
       self.token = token.__dict__
    
    @staticmethod
    def hash_pw(pw):
        return hashlib.md5(pw.encode()).hexdigest()

class UserCollection:
    _userCollection = None
    def __init__(self, db:Database):
        if UserCollection._userCollection is None:
            UserCollection._userCollection = db.users
        else:
            raise Exception("user collection is already init. Call get_instance() instead")
        
    @staticmethod
    def get_instance():
        return UserCollection._userCollection
    
    @staticmethod
    @db_err_handler
    def insert_user(newUser:UserModel):
        return UserCollection._userCollection.insert_one(newUser.__dict__)
    
    @staticmethod
    @db_err_handler
    def find_user_by_username(user_name):
        return UserCollection._userCollection.find_one({"user_name" : user_name})
    
    @staticmethod
    @db_err_handler
    def renew_token_by_username(user_name):
        new_expiration = TokenModel.get_latest_exp()
        new_digest = jwt.encode({"user_name" : user_name, "exp" : new_expiration}, os.getenv("SECRET_KEY"),algorithm="HS256")

        return UserCollection._userCollection.update_one({"user_name":user_name}, {"$set" : {"token.digest" : new_digest, "token.exp" : new_expiration}})
    
    @staticmethod
    @db_err_handler
    def push_topic_of_username(user_name, topic_id):
        return UserCollection._userCollection.update_one({"user_name":user_name}, {"$push" : {"topics" : str(topic_id)}})
    
    @staticmethod
    @db_err_handler
    def del_topic_of_username(user_name, topic_id):
        return UserCollection._userCollection.update_one({"user_name":user_name}, {"$pull" : {"topics" : str(topic_id)}})