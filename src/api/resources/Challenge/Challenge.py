from os import remove
from os.path import join

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

class Challenges(Resource):
    @marshal_with(mfields)
    def get(self, page_num, limit=3):
        if page_num==0: return {"error" : "page_num > 0"}
        # todo: hide ans before sending back to client
        res = challenge_collection.get_challenges(int(page_num), limit)
        return {"payload" : jsonize_cursor(res)}

class ChallengeResource(Resource):

    @marshal_with(mfields)
    def get(self):
        args = write_parser.parse_args()
        challenge_id = str(args['challenge_id'])
        res = challenge_collection.get_challenge(challenge_id)
        if res is None: return {"payload" : "", "message" : "not found"}

        res['_id'] = str(res['_id'])
        return {"payload" : res}

    # upload an empty topisc
    @marshal_with(mfields)
    @protected_by_token
    def post(self, user_name):
        args = create_parser.parse_args()
        challenge_name, challenge_desc = args['challenge_name'], args['challenge_desc']
        challenge_vm = args['challenge_vm']
        banner_img = args['banner_img']

        challenge_file_obj = VmFile(challenge_vm)
        challenge_file_obj.save()

        banner_file_obj = ImgFile(banner_img)
        banner_file_obj.save()

        try:
            with client.start_session() as session:
                with session.start_transaction():
                    new_challenge = ChallengeModel(user_name, 
                                        challenge_name, 
                                        challenge_desc, 
                                        join(challenge_file_obj.get_subfolder(), challenge_file_obj.file_name), 
                                        join(banner_file_obj.get_subfolder(), banner_file_obj.file_name))
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
                    BaseFile(None).delete(fp)

                with client.start_session() as session:
                    with session.start_transaction():
                        challenge_collection.del_challenge(challenge_id)
                        user_collection.del_challenge(user_name, challenge_id)
                return {"message" : "deleted challenge successfully"}
            except Exception as e:
                return {"error" : e}, 500

        return {"error" : "Unauthorized action"}, 401
