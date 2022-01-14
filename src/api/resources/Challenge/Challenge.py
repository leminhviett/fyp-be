from os import remove
import re
from src.api.models import *
from src.api.middlewares.protector import protected_by_token
from flask_restful import Resource, marshal_with, reqparse
from src.utils.utils import get_response_format
from src.api.resources.Challenge import *
from src.api.models import client
from .helper import helper_check_ownership, gen_unique_filename
from src.utils.storage import *
from werkzeug.datastructures import FileStorage

create_parser = reqparse.RequestParser()
create_parser.add_argument("challenge_name", type=str, help="challenge name is reuqired", required=True)
create_parser.add_argument("challenge_desc", type=str, help="challenge desc is reuqired", required=True)

create_parser.add_argument("banner_img", type=FileStorage, location='files')
create_parser.add_argument("challenge_vm", type=FileStorage, location='files')


write_parser = reqparse.RequestParser()
write_parser.add_argument("challenge_id", type=str, help="challenge id is reuqired", required=True)

mfields = get_response_format()

class ChallengeResource(Resource):

    @marshal_with(mfields)
    def get(self):
        return {"payload" : challenge_collection.get_topic_by_id(id)}

    # upload an empty topisc
    @marshal_with(mfields)
    @protected_by_token
    def post(self, user_name):
        args = create_parser.parse_args()
        challenge_name, challenge_desc = args['challenge_name'], args['challenge_desc']
        challenge_vm = args['challenge_vm']
        banner_img = args['banner_img']

        challenge_file_obj = VmFile(challenge_vm, user_name)
        challenge_file_obj.save()

        banner_file_obj = ImgFile(banner_img, user_name)
        banner_file_obj.save()

        try:
            with client.start_session() as session:
                with session.start_transaction():
                    new_challenge = ChallengeModel(user_name, challenge_name, challenge_desc, challenge_file_obj.get_full_loc(), banner_file_obj.get_full_loc())
                    result = challenge_collection.insert_challenge(new_challenge)
                    result2 = user_collection.push_challenge(user_name, str(result.inserted_id))
            
            if result2:
                return {"message" : "successfully added challenge"}
            
        except Exception as e:
            return {"error" : e}, 500
        # return {"message" : "gud"}
    
    @marshal_with(mfields)
    @protected_by_token
    def delete(self, user_name):
        args = write_parser.parse_args()
        challenge_id = str(args['challenge_id'])

        if helper_check_ownership(user_name, challenge_id):
            try:
                # remove file in storage
                target_challenge = challenge_collection.get_challenge(challenge_id)
                removed_files = [target_challenge['challenge_vm'], target_challenge['img_loc']]

                for task in target_challenge['tasks']:
                    removed_files.append(task['img_loc'])
                
                for fp in removed_files:
                    try:
                        os.remove(fp)
                    except OSError:
                        pass

                with client.start_session() as session:
                    with session.start_transaction():
                        challenge_collection.del_challenge(challenge_id)
                        user_collection.del_challenge(user_name, challenge_id)
                return {"message" : "deleted challenge successfully"}
            except Exception as e:
                return {"error" : e}, 500

        return {"error" : "Unauthorized action"}, 401
