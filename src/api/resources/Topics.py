from flask_restful import Resource, marshal_with, reqparse
from src.api.models import *
from src.api.middlewares import protector
from src.utils.utils import get_response_format
from src.api.models.index import client

def helper_check_ownership(user_name, topic_id):
    result = TopicCollection.get_topic_by_id(topic_id)
    if result:
        if result['author_name'] == user_name:
            return True
    
    return False

topic_create_parser = reqparse.RequestParser()
topic_create_parser.add_argument("topic_name", type=str, help="topic name is reuqired", required=True)
topic_create_parser.add_argument("topic_desc", type=str, help="topic desc is reuqired", required=True)
topic_create_parser.add_argument("banner_img", type=str)

topic_write_parser = reqparse.RequestParser()
topic_write_parser.add_argument("topic_id", type=str, help="topic id is reuqired", required=True)

mfields = get_response_format()

class Topics(Resource):
    @marshal_with(mfields)
    def get(self):
        return {"payload" : jsonize_cursor(TopicCollection.get_topics())}

class Topic(Resource):

    @marshal_with(mfields)
    def get(self):
        return {"payload" : TopicCollection.get_topic_by_id(id)}

    # upload an empty topisc
    @marshal_with(mfields)
    @protector.protected_by_token
    def post(self, user_name):
        args = topic_create_parser.parse_args()
        topic_name, topic_desc, banner_img = args['topic_name'], args['topic_desc'], args['banner_img']

        try:
            with client.start_session() as session:
                with session.start_transaction():
                    result = TopicCollection.insert_topic(TopicModel(user_name, topic_name, topic_desc, banner_img))
                    result2 = UserCollection.push_topic_of_username(user_name, str(result.inserted_id))
            if result2:        
                return {"message" : "successfully added topic"}
        except Exception as e:
            return {"error" : e}, 500
        # return {"message" : "gud"}
    
    @marshal_with(mfields)
    @protector.protected_by_token
    def delete(self, user_name):
        args = topic_write_parser.parse_args()
        topic_id = str(args['topic_id'])

        if helper_check_ownership(user_name, topic_id):
            try:
                with client.start_session() as session:
                    with session.start_transaction():
                        TopicCollection.delete_topic_by_id(topic_id)
                        UserCollection.del_topic_of_username(user_name, topic_id)
                return {"message" : "deleted topic successfully"}
            except Exception as e:
                return {"error" : e}, 500

        return {"error" : "Unauthorized action"}, 401
    
task_parser = reqparse.RequestParser()
task_parser.add_argument("topic_id", type=str, help="topic_id is reuqired", required=True)
task_parser.add_argument("task_idx", type=int)
task_parser.add_argument("task_data", type=dict)


#TODO: when the Storage upload is ready. Remember to delete remote file,
# whenever task is updated/ or deleted

class Task(Resource):

    @staticmethod
    def parse_task(task_data):
        attrs = ["desc", "ques", "ans", "img_loc"]
        for attr in attrs:
            if attr in task_data:
                # print(f"{attr} checked")
                continue
            return None
        
        desc, ques, ans, img_loc = task_data['desc'], task_data['ques'], task_data['ans'], task_data['img_loc']
        return TaskModel(desc, ques, ans, img_loc)

    @marshal_with(mfields)
    @protector.protected_by_token
    def post(self, user_name):
        args = task_parser.parse_args()
        topic_id, task_data = args['topic_id'], args['task_data']

        if helper_check_ownership(user_name, topic_id):
            task_model = self.parse_task(task_data)

            if task_model is None:
                return {"error" : "Invalid task data"}, 400
            result = TopicCollection.add_task_by_topic_id(topic_id, task_model)
            if result is None:
                return {"error" : "DB error"}, 500

            return {"message":"new task added"}

        return {"error" : "Unauthorized action"}, 401
    
    @marshal_with(mfields)
    @protector.protected_by_token
    def patch(self, user_name):
        args = task_parser.parse_args()
        topic_id, task_data, task_idx = args['topic_id'], args['task_data'], args['task_idx']

        if helper_check_ownership(user_name, topic_id):
            task_model = self.parse_task(task_data)

            if task_model is None:
                return {"error" : "Invalid task data"}, 401
            result = TopicCollection.update_task_by_topic_id(topic_id, task_idx, task_model)
            if result is None:
                return {"error" : "DB error"}, 500
            return {"message":"task updated"}

        return {"error" : "Unauthorized action"}, 401


    @marshal_with(mfields)
    @protector.protected_by_token
    def delete(self, user_name):
        args = task_parser.parse_args()
        topic_id, task_idx = args['topic_id'], args['task_idx']

        # delete in array
        if helper_check_ownership(user_name, topic_id):
            result = TopicCollection.del_task_topic_by_id(topic_id, task_idx)
            if result:
                return {"message":"task deleted"}
            return {"error" : "DB error"}, 500
        return {"error" : "Unauthorized action"}, 401
