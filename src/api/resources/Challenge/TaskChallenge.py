from calendar import c
from flask_restful import Resource, marshal_with, reqparse
from src.api.models import *
from src.api.middlewares import protector
from src.utils.utils import get_response_format
from src.api.resources.Challenge import *
from .helper import helper_check_ownership
import werkzeug
from src.utils.storage import *

mfields = get_response_format()

task_parser = reqparse.RequestParser()
task_parser.add_argument("challenge_id", type=str, help="challenge_id is reuqired", required=True)
task_parser.add_argument("task_idx", type=int)
task_parser.add_argument("task_data", type=dict)


#TODO: when the Storage upload is ready. Remember to delete remote file,
# whenever task is updated/ or deleted

class TaskChallenge(Resource):
    @staticmethod
    def gen_img_fn(challenge_id):
        return f"{challenge_id}-{uuid.uuid4()}.png"

    @staticmethod
    def parse_task(task_data, challenge_id):
        attrs = ["caption", "img_data"]
        for attr in attrs:
            if attr in task_data:
                # print(f"{attr} checked")
                continue
            return None
        
        caption, img_data = task_data['caption'], task_data['img_data']

        img_encoded = ImgEncoded(img_data.encode(), TaskChallenge.gen_img_fn(challenge_id) )
        img_encoded.save()

        return ChallengeTaskModel(caption, img_encoded.full_loc)

    @marshal_with(mfields)
    @protector.protected_by_token
    def post(self, user_name):
        args = task_parser.parse_args()
        challenge_id, task_data = args['challenge_id'], args['task_data']

        if helper_check_ownership(user_name, challenge_id):
            task_model = self.parse_task(task_data, challenge_id)

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
            task_model = self.parse_task(task_data, challenge_id)

            # remove all file loc in storage
            target_challenge = challenge_collection.get_challenge(challenge_id)
            try:
                os.remove(target_challenge['tasks'][task_idx]['img_loc'])
            except OSError:
                pass

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
            
        if helper_check_ownership(user_name, challenge_id):
            # remove all file loc in storage
            target_challenge = challenge_collection.get_challenge(challenge_id)
            try:
                os.remove(target_challenge['tasks'][task_idx]['img_loc'])
            except OSError:
                pass

            result = challenge_collection.del_task(challenge_id, task_idx)
            if result:
                return {"message":"task deleted"}
            return {"error" : "DB error"}, 500
        return {"error" : "Unauthorized action"}, 401
