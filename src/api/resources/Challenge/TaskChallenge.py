from flask_restful import Resource, marshal_with, reqparse
from src.api.models import *
from src.api.middlewares import protector
from src.utils.utils import get_response_format
from src.api.resources.Challenge import *
from .helper import helper_check_ownership

mfields = get_response_format()

task_parser = reqparse.RequestParser()
task_parser.add_argument("challenge_id", type=str, help="challenge_id is reuqired", required=True)
task_parser.add_argument("task_idx", type=int)
task_parser.add_argument("task_data", type=dict)

#TODO: when the Storage upload is ready. Remember to delete remote file,
# whenever task is updated/ or deleted

class TaskChallenge(Resource):

    @staticmethod
    def parse_task(task_data):
        attrs = ["caption", "img_loc"]
        for attr in attrs:
            if attr in task_data:
                # print(f"{attr} checked")
                continue
            return None
        
        caption, img_loc = task_data['caption'], task_data['img_loc']
        return ChallengeTaskModel(caption, img_loc)

    @marshal_with(mfields)
    @protector.protected_by_token
    def post(self, user_name):
        args = task_parser.parse_args()
        challenge_id, task_data = args['challenge_id'], args['task_data']

        if helper_check_ownership(user_name, challenge_id):
            task_model = self.parse_task(task_data)

            if task_model is None:
                return {"error" : "Invalid task data"}, 400
            result = challenge_collection.add_task(challenge_id, task_model)
            if result is None:
                return {"error" : "DB error"}, 500

            return {"message":"new task added"}

        return {"error" : "Unauthorized action"}, 401
    
    @marshal_with(mfields)
    @protector.protected_by_token
    def patch(self, user_name):
        args = task_parser.parse_args()
        challenge_id, task_data, task_idx = args['challenge_id'], args['task_data'], args['task_idx']

        if challenge_collection.get_len_tasks(challenge_id) - 1 < task_idx:
            return {"error" : 'task idx not exist'}

        if helper_check_ownership(user_name, challenge_id):
            task_model = self.parse_task(task_data)

            if task_model is None:
                return {"error" : "Invalid task data"}, 401
            result = challenge_collection.update_task(challenge_id, task_idx, task_model)
            if result is None:
                return {"error" : "DB error"}, 500
            return {"message":"task updated"}

        return {"error" : "Unauthorized action"}, 401


    @marshal_with(mfields)
    @protector.protected_by_token
    def delete(self, user_name):
        args = task_parser.parse_args()
        challenge_id, task_idx = args['challenge_id'], args['task_idx']

        if challenge_collection.get_len_tasks(challenge_id) - 1 < task_idx:
            return {"error" : 'task idx not exist'}
            
        # delete in array
        if helper_check_ownership(user_name, challenge_id):
            result = challenge_collection.del_task(challenge_id, task_idx)
            if result:
                return {"message":"task deleted"}
            return {"error" : "DB error"}, 500
        return {"error" : "Unauthorized action"}, 401
