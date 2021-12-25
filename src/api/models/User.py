from pymongo.collection import ReturnDocument
from pymongo.database import Database
import hashlib, jwt, os
from .Token import TokenModel
from .utils import db_err_handler

class UserModel:
    def __init__(self, user_name, pw, token:TokenModel,topics=[], challenges=[]):
       self.user_name = user_name
       self.hashed_pw = self.hash_pw(pw)
       self.topics = topics
       self.challenges = challenges
       self.token = token.__dict__
    
    @classmethod
    def hash_pw(cls, pw):
        return hashlib.md5(pw.encode()).hexdigest()

@db_err_handler
class UserCollection:
    def __init__(self, db:Database) -> None:
        self.collection = db.users
    
    def insert_user(self, newUser:UserModel):
        return self.collection.insert_one(newUser.__dict__)
    
    def find_user_by_username(self, user_name):
        return self.collection.find_one({"user_name" : user_name})
    
    def renew_token(self, user_name):
        new_expiration = TokenModel.get_latest_exp()
        new_digest = jwt.encode({"user_name" : user_name, "exp" : new_expiration}, os.getenv("SECRET_KEY"),algorithm="HS256")

        return self.collection.find_one_and_update({"user_name":user_name}, {"$set" : {"token.digest" : new_digest, "token.exp" : new_expiration}}, return_document=ReturnDocument.AFTER)
    
    def push_topic(self, user_name, topic_id):
        return self.collection.update_one({"user_name":user_name}, {"$push" : {"topics" : str(topic_id)}})
    
    def del_topic(self, user_name, topic_id):
        return self.collection.update_one({"user_name":user_name}, {"$pull" : {"topics" : str(topic_id)}})

    def push_challenge(self, user_name, challenge_id):
        return self.collection.update_one({"user_name":user_name}, {"$push" : {"challenges" : str(challenge_id)}})
    
    def del_challenge(self, user_name, challenge_id):
        return self.collection.update_one({"user_name":user_name}, {"$pull" : {"challenges" : str(challenge_id)}})
