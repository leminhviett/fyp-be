from flask_restful import Resource, marshal_with, reqparse
from src.api.models import *
from src.api.middlewares import protector
from src.utils.utils import get_response_format
from .helper import helper_check_ownership

mfields = get_response_format()

task_parser = reqparse.RequestParser()
task_parser.add_argument("section_idx", type=int, help="section idx is reuqired", required=True)
task_parser.add_argument("topic_id", type=str, help="topic id is reuqired", required=True)
task_parser.add_argument("task_idx", type=int)
task_parser.add_argument("task_data", type=dict)

#TODO: when the Storage upload is ready. Remember to delete remote file,
# whenever task is updated/ or deleted

class TaskTopic(Resource):

    @staticmethod
    def parse_task(task_data):
        attrs = ["desc", "ques", "ans", "img_loc"]
        for attr in attrs:
            if attr in task_data:
                # print(f"{attr} checked")
                continue
            return None
        
        desc, ques, ans, img_loc = task_data['desc'], task_data['ques'], task_data['ans'], task_data['img_loc']
        return TopicTaskModel(desc, ques, ans, img_loc)

    @marshal_with(mfields)
    @protector.protected_by_token
    def post(self, user_name):
        args = task_parser.parse_args()
        section_idx, topic_id, task_data = args['section_idx'], args['topic_id'], args['task_data']

        if topic_collection.get_len_section(topic_id) - 1 < section_idx:
            return {"error" : "section idx not exist"}

        if helper_check_ownership(user_name, topic_id):
            task_model = self.parse_task(task_data)

            if task_model is None:
                return {"error" : "Invalid task data"}, 400
            result = topic_collection.add_task(topic_id, section_idx, task_model)
            if result is None:
                return {"error" : "DB error"}, 500

            return {"message":"new task added"}

        return {"error" : "Unauthorized action"}, 401
    
    @marshal_with(mfields)
    @protector.protected_by_token
    def patch(self, user_name):
        args = task_parser.parse_args()
        topic_id, task_data, task_idx, section_idx = args['topic_id'], args['task_data'], args['task_idx'], args['section_idx']

        if topic_collection.get_len_section(topic_id) - 1 < section_idx:
            return {"error" : "section idx not exist"}

        if topic_collection.get_len_task(topic_id, section_idx) - 1 < task_idx:
            return {"error" : "task idx not exist"}

        if helper_check_ownership(user_name, topic_id):
            task_model = self.parse_task(task_data)
            print(task_model.to_dict())
            if task_model is None:
                return {"error" : "Invalid task data"}, 401
            result = topic_collection.update_task(topic_id, section_idx, task_idx, task_model)
            if result is None:
                return {"error" : "DB error"}, 500
            return {"message":"task updated"}

        return {"error" : "Unauthorized action"}, 401


    @marshal_with(mfields)
    @protector.protected_by_token
    def delete(self, user_name):
        args = task_parser.parse_args()
        topic_id, section_idx, task_idx = args['topic_id'], args['section_idx'], args['task_idx']

        if topic_collection.get_len_section(topic_id) - 1 < section_idx:
            return {"error" : "section idx not exist"}
        
        if topic_collection.get_len_task(topic_id, section_idx) - 1 < task_idx:
            return {"error" : "task idx not exist"}

        # delete in array
        if helper_check_ownership(user_name, topic_id):
            result = topic_collection.del_task_topic_by_id(topic_id, task_idx)
            if result:
                return {"message":"task deleted"}
            return {"error" : "DB error"}, 500
        return {"error" : "Unauthorized action"}, 401
