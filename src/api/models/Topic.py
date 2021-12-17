from typing import List
from pymongo.database import Database
from bson.objectid import ObjectId
from src.api.models import db_err_handler

class TaskModel:
    def __init__(self, desc, ques, ans, img_loc:str):
        self.desc = desc
        self.ques = ques
        self.ans = ans
        self.img_loc = img_loc

    def to_dict(self):
        return self.__dict__
            
class SectionModel:
    MAX_LEN_TASK = 15

    def __init__(self, heading, tasks:List[TaskModel] = []):
        self.heading = heading
        self.tasks = tasks
    
    def to_dict(self):
        temp = [ele.to_dict() for ele in self.tasks]
        return {"heading" : self.heading, "tasks" : temp}

class TopicModel:
    def __init__(self, user_name, topic_name, desc, img_loc=None, sections:List[SectionModel] = []) -> None:
        self.author_name = user_name
        self.topic_name = topic_name
        self.topic_desc = desc
        self.sections = sections
        self.banner_img = img_loc

    def to_dict(self):
        temp = [ele.to_dict() for ele in self.sections]
        return {
            "author_name" : self.author_name,
            "topic_name": self.topic_name,
            "topic_desc" : self.topic_desc,
            "sections" : temp,
            "banner_img" : self.banner_img
        }

class TopicCollection:
    _topicCollection = None
    def __init__(self, db:Database):
        if TopicCollection._topicCollection is None:
            TopicCollection._topicCollection = db.topics
        else:
            raise Exception("topic collection is already init. Call get_instance() instead")
    
    @db_err_handler
    def get_instance():
        return TopicCollection._topicCollection
    
    @db_err_handler
    def insert_topic(new_topic:TopicModel):
        return TopicCollection._topicCollection.insert_one(new_topic.to_dict())
    
    @db_err_handler
    def get_topic_by_id(topic_id:str):
        return TopicCollection._topicCollection.find_one({"_id":ObjectId(topic_id)})
    
    @db_err_handler
    def get_topics():
        return TopicCollection._topicCollection.find()

    @db_err_handler
    def add_task_by_topic_id(topic_id, task:TaskModel):
        return TopicCollection._topicCollection.update_one({"_id" : ObjectId(topic_id)}, {"$push" : {"sections" : task.to_dict()}})
    
    @db_err_handler
    def update_task_by_topic_id(topic_id, task_idx, task:TaskModel):
        return TopicCollection._topicCollection.update_one({"_id" : ObjectId(topic_id)}, {"$set" : {f"sections.{task_idx}" : task.to_dict()}})
    
    @db_err_handler
    def delete_topic_by_id(topic_id:str):
        return TopicCollection._topicCollection.delete_one({"_id" : ObjectId(topic_id)})

    @db_err_handler
    def del_task_topic_by_id(topic_id, task_idx):
        result1 = TopicCollection._topicCollection.update_one({"_id" : ObjectId(topic_id)}, {"$unset" : {f"sections.{task_idx}" : ""}})
        if result1:
            result2 = TopicCollection._topicCollection.update_one({"_id" : ObjectId(topic_id)}, {"$pull" : {f"sections" : None}})
        else:
            return None
        
        return result2