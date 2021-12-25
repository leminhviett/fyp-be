from typing import List
from pymongo.database import Database
from bson.objectid import ObjectId

from src.api.models.utils import db_err_handler

class ChallengeTaskModel:
    def __init__(self, caption, img_loc):
        self.caption = caption
        self.img_loc = img_loc

    def to_dict(self):
        return self.__dict__

class ChallengeModel:
    def __init__(self, user_name, challenge_name, desc, img_loc=None, tasks:List[ChallengeTaskModel] = []) -> None:
        self.author_name = user_name
        self.challenge_name = challenge_name
        self.challenge_desc = desc
        self.img_loc = img_loc
        self.tasks = tasks

    def to_dict(self):
        temp = [ele.to_dict() for ele in self.tasks]
        return {
            "author_name" : self.author_name,
            "challenge_name": self.challenge_name,
            "challenge_desc" : self.challenge_desc,
            "tasks" : temp,
            "img_loc" : self.img_loc
        }


class ChallengeCollection:
    _challengeCollection = None
    def __init__(self, db:Database):
        if ChallengeCollection._challengeCollection is None:
            ChallengeCollection._challengeCollection = db.challenges
        else:
            raise Exception("user collection is already init. Call get_instance() instead")

    @classmethod
    def get_instance(cls):
        return cls._challengeCollection
    
    @classmethod
    @db_err_handler
    def del_challenge_by_id(cls, challenge_id:str):
        return cls._challengeCollection.delete_one({"_id" : ObjectId(challenge_id)})
    
    @classmethod
    @db_err_handler
    def get_challenge_by_id(cls, challenge_id:str):
        return cls._challengeCollection.find_one({"_id" : ObjectId(challenge_id)})

    @classmethod
    @db_err_handler
    def insert_challenge(cls, new_challenge:ChallengeModel):
        return cls._challengeCollection.insert_one(new_challenge.to_dict())

    @classmethod
    @db_err_handler
    def add_task_by_challenge_id(cls, challengeId, task:ChallengeTaskModel):
        return cls._challengeCollection.update_one({"_id" : ObjectId(challengeId)}, {"$push" : {"tasks" : task.to_dict()}})

    @classmethod
    @db_err_handler
    def update_task_by_topic_id(cls, topic_id, task_idx, task:ChallengeTaskModel):
        return cls._topicCollection.update_one({"_id" : ObjectId(topic_id)}, {"$set" : {f"sections.{task_idx}" : task.to_dict()}})
    
