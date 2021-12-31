from typing import List
from pymongo.database import Database
from bson.objectid import ObjectId
from src.api.models import db_err_handler


class TopicTaskModel:
    def __init__(self, desc, ques, ans, img_loc:str):
        self.desc = desc
        self.ques = ques
        self.ans = ans
        self.img_loc = img_loc

    def to_dict(self):
        return self.__dict__
            
class TopicSectionModel:
    MAX_LEN_TASK = 15

    def __init__(self, heading, tasks:List[TopicTaskModel] = []):
        self.heading = heading
        self.tasks = tasks
    
    def to_dict(self):
        temp = [ele.to_dict() for ele in self.tasks]
        return {"heading" : self.heading, "tasks" : temp}

class TopicModel:
    def __init__(self, user_name, topic_name, desc, img_loc=None, sections:List[TopicSectionModel] = []) -> None:
        self.author_name = user_name
        self.topic_name = topic_name
        self.topic_desc = desc
        self.sections = sections
        self.banner_img = img_loc
        self.published = False

    def to_dict(self):
        temp = [ele.to_dict() for ele in self.sections]
        return {
            "author_name" : self.author_name,
            "topic_name": self.topic_name,
            "topic_desc" : self.topic_desc,
            "sections" : temp,
            "banner_img" : self.banner_img,
            "published" : self.published
        }

@db_err_handler
class TopicCollection:
    
    def get_len_section(self,topic_id):
        res = self.collection.find_one({"_id" : ObjectId(topic_id)})
        return len(res['sections'])

    def get_len_task(self, topic_id, section_idx:int):
        res = self.collection.find_one({"_id" : ObjectId(topic_id)})
        if len(res['sections']) - 1 >= section_idx:
            print(len(res['sections'][section_idx]['tasks']))
            return len(res['sections'][section_idx]['tasks'])
        else:
            return -1

    def __init__(self, db:Database):
        self.collection = db.topics
    
    def insert_topic(self, new_topic:TopicModel):
        return self.collection.insert_one(new_topic.to_dict())
    
    def get_topic(self, topic_id:str):
        return self.collection.find_one({"_id":ObjectId(topic_id)})
    
    def get_topics(self):
        return self.collection.find()

    def set_topic_published(self, topic_id:str):
        return self.collection.update_one({"_id" : ObjectId(topic_id)}, {"$set" : {"published" : True}})

    def del_topic(self, topic_id:str):
        return self.collection.delete_one({"_id" : ObjectId(topic_id)})

    def add_section(self, topic_id, section:TopicSectionModel):
        return self.collection.update_one({"_id" : ObjectId(topic_id)}, {"$push" : {"sections" : section.to_dict()}})
    
    def update_section_heading(self, topic_id, section_idx, section_heading:str):
        return self.collection.update_one({"_id" : ObjectId(topic_id)}, {"$set" : {f"sections.{section_idx}.heading" : section_heading}})
    
    def del_section(self, topic_id, section_idx):
        result1 = self.collection.update_one({"_id" : ObjectId(topic_id)}, {"$unset" : {f"sections.{section_idx}" : ""}})
        if result1:
            result2 = self.collection.update_one({"_id" : ObjectId(topic_id)}, {"$pull" : {f"sections" : None}})
        else:
            return None
        
        return result2
    
    def add_task(self, topic_id, section_idx, task:TopicTaskModel):
        return self.collection.update_one({"_id" : ObjectId(topic_id)}, {"$push" : {f"sections.{section_idx}.tasks" : task.to_dict()}})

    def update_task(self, topic_id, section_idx, task_idx, task:TopicTaskModel):
        return self.collection.update_one({"_id" : ObjectId(topic_id)}, {"$set" : {f"sections.{section_idx}.tasks.{task_idx}" : task.to_dict()}})
    
    def del_task(self, topic_id, section_idx, task_idx):
        result1 = self.collection.update_one({"_id" : ObjectId(topic_id)}, {"$unset" : {f"sections.{section_idx}.tasks.{task_idx}" : ""}})
        if result1:
            result2 = self.collection.update_one({"_id" : ObjectId(topic_id)}, {"$pull" : {f"sections.{section_idx}.tasks" : None}})
        else:
            return None
        
        return result2
