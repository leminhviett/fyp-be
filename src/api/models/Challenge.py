from typing import List
from pymongo.database import Database

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
        self.banner_img = img_loc
        self.tasks = tasks

    def to_dict(self):
        temp = [ele.to_dict() for ele in self.tasks]
        return {
            "author_name" : self.author_name,
            "challenge_name": self.challenge_name,
            "challenge_desc" : self.challenge_desc,
            "tasks" : temp,
            "img_loc" : self.banner_img
        }



class ChallengeCollection:
    _challengeCollection = None
    def __init__(self, db:Database):
        if ChallengeCollection._challengeCollection is None:
            ChallengeCollection._challengeCollection = db.users
        else:
            raise Exception("user collection is already init. Call get_instance() instead")
        