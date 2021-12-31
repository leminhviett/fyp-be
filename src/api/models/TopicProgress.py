from collections import defaultdict
from pymongo.database import Database

class TopicProgressModel:
    def __init__(self, topic_id, learner_id) -> None:
        self.topic_id = topic_id
        self.learner_id = learner_id
        self.done = defaultdict(list) # key is section idx, value: is list of finished tasks idx

    def to_dict(self):
        return {"topic_id" : self.topic_id, "learner_id" : self.learner_id, "done" : self.done}

class TopicProgessCollection:
    def __init__(self, db:Database) -> None:
        self.collection = db.topic_progess
    
    def get_progess(self, topic_id, learner_id):
        return self.collection.find_one({"topic_id" : topic_id, "learner_id" : learner_id})

    def add_progress(self, progress:TopicProgressModel):
        return self.collection.insert_one(progress.to_dict())

    def update_progress(self, topic_id, learner_id, section_idx, topic_idx):
        return self.collection.update_one({"topic_id" : topic_id, "learner_id" : learner_id}, {"$push" : {f"done.{section_idx}" : topic_idx}})

    def del_progress(self, topic_id, learner_id):
        return self.collection.delete_one({"topic_id" : topic_id, "learner_id" : learner_id})
