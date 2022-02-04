from flask_restful import Resource, marshal_with, reqparse
from src.api.models import *
from src.api.middlewares import protector
from src.utils.utils import get_response_format
from src.utils.storage import ImgEncoded
from .helper import *
import uuid

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
    def gen_img_fn(topic_id):
        return f"{topic_id}-{uuid.uuid4()}.png"
    
    @staticmethod
    def del_file_task(topic_id, section_idx, task_idx):
        target_topic = topic_collection.get_topic(topic_id)
        target_task = target_topic['sections'][section_idx]['tasks'][task_idx]

        try:
            ImgEncoded('', '').delete(target_task['img_loc'])
        except OSError:
            pass
    
    @staticmethod
    def parse_task(topic_id, task_data):
        attrs = ["desc", "ques", "ans", "img_data"]
        for attr in attrs:
            if attr in task_data:
                # print(f"{attr} checked")
                continue
            return None
        
        desc, ques, ans, img_data = task_data['desc'], task_data['ques'], task_data['ans'], task_data['img_data']

        if not img_data: return TopicTaskModel(desc, ques, ans, "")

        try:
            img_encoded = ImgEncoded(img_data, TaskTopic.gen_img_fn(topic_id))
            img_encoded.save()
            saved_loc = os.path.join(img_encoded.sub_folder, img_encoded.file_name)
        except Exception as e:
            print(f"Error {e} during encoding img")
            
        
        return TopicTaskModel(desc, ques, ans, saved_loc)

    @marshal_with(mfields)
    @helper_check_is_published
    @protector.protected_by_token
    def post(self, user_name):
        args = task_parser.parse_args()
        section_idx, topic_id, task_data = args['section_idx'], args['topic_id'], args['task_data']

        if topic_collection.get_len_section(topic_id) - 1 < section_idx:
            return {"error" : "section idx not exist"}

        if helper_check_ownership(user_name, topic_id):
            task_model = self.parse_task(topic_id, task_data)

            if task_model is None:
                return {"error" : "Invalid task data"}, 400
            result = topic_collection.add_task(topic_id, section_idx, task_model)
            if result is None:
                return {"error" : "DB error"}, 500

            return {"message":"new task added"}

        return {"error" : "Unauthorized action"}, 401
    
    @marshal_with(mfields)
    @helper_check_is_published
    @protector.protected_by_token
    def patch(self, user_name):
        args = task_parser.parse_args()
        topic_id, task_data, task_idx, section_idx = args['topic_id'], args['task_data'], args['task_idx'], args['section_idx']

        if topic_collection.get_len_section(topic_id) - 1 < section_idx:
            return {"error" : "section idx not exist"}

        if topic_collection.get_len_task(topic_id, section_idx) - 1 < task_idx:
            return {"error" : "task idx not exist"}

        if helper_check_ownership(user_name, topic_id):
            task_model = self.parse_task(topic_id, task_data)

            # old file task
            TaskTopic.del_file_task(topic_id, section_idx, task_idx)

            if task_model is None:
                return {"error" : "Invalid task data"}, 401
            result = topic_collection.update_task(topic_id, section_idx, task_idx, task_model)
            if result is None:
                return {"error" : "DB error"}, 500
            return {"message":"task updated"}

        return {"error" : "Unauthorized action"}, 401


    @marshal_with(mfields)
    @helper_check_is_published
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
            target_topic = topic_collection.get_topic(topic_id)

            # old file task
            TaskTopic.del_file_task(topic_id, section_idx, task_idx)

            result = topic_collection.del_task(topic_id, section_idx, task_idx)
            if result:
                return {"message":"task deleted"}
            return {"error" : "DB error"}, 500
        return {"error" : "Unauthorized action"}, 401
