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
    def __init__(self, user_name, challenge_name, desc, vm_loc:str, img_loc=None, tasks:List[ChallengeTaskModel] = []) -> None:
        self.author_name = user_name
        self.challenge_name = challenge_name
        self.challenge_desc = desc
        self.challenge_vm = vm_loc
        self.img_loc = img_loc
        self.tasks = tasks

    def to_dict(self):
        temp = [ele.to_dict() for ele in self.tasks]
        return {
            "author_name" : self.author_name,
            "challenge_name": self.challenge_name,
            "challenge_desc" : self.challenge_desc,
            "challenge_vm": self.challenge_vm,
            "img_loc" : self.img_loc,
            "tasks" : temp
        }


class ChallengeCollection:
    def __init__(self, db:Database):
        self.collection = db.challenges
    
    def get_len_tasks(self, challenge_id):
        res = self.collection.find_one({"_id" : ObjectId(challenge_id)})
        if res is None:
            return -1
        return len(res['tasks'])

    @db_err_handler
    def del_challenge(self, challenge_id:str):
        return self.collection.delete_one({"_id" : ObjectId(challenge_id)})
    
    @db_err_handler
    def get_challenge(self, challenge_id:str):
        return self.collection.find_one({"_id" : ObjectId(challenge_id)})

    @db_err_handler
    def insert_challenge(self, new_challenge:ChallengeModel):
        return self.collection.insert_one(new_challenge.to_dict())

    @db_err_handler
    def add_task(self, challengeId, task:ChallengeTaskModel):
        return self.collection.update_one({"_id" : ObjectId(challengeId)}, {"$push" : {"tasks" : task.to_dict()}})

    @db_err_handler
    def update_task(self, challenge_id, task_idx, task:ChallengeTaskModel):
        return self.collection.update_one({"_id" : ObjectId(challenge_id)}, {"$set" : {f"tasks.{task_idx}" : task.to_dict()}})
    
    @db_err_handler
    def del_task(self, challenge_id, task_idx):
        result1 = self.collection.update_one({"_id" : ObjectId(challenge_id)}, {"$unset" : {f"tasks.{task_idx}" : ""}})
        if result1:
            result2 = self.collection.update_one({"_id" : ObjectId(challenge_id)}, {"$pull" : {f"tasks" : None}})
        else:
            return None
        
        return result2