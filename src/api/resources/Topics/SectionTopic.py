from flask_restful import Resource, marshal_with, reqparse
from src.api.models import *
from src.api.middlewares import protector
from src.utils.utils import get_response_format
from .helper import helper_check_ownership

mfields = get_response_format()

section_parser = reqparse.RequestParser()
section_parser.add_argument("topic_id", type=str, help="topic id is reuqired", required=True)
section_parser.add_argument("section_heading", type=str)
section_parser.add_argument("section_idx", type=int)

#TODO: when the Storage upload is ready. Remember to delete remote file,
# whenever section is updated/ or deleted

class SectionTopic(Resource):

    @marshal_with(mfields)
    @protector.protected_by_token
    def post(self, user_name):
        args = section_parser.parse_args()
        topic_id, section_heading = args['topic_id'], args['section_heading']

        if helper_check_ownership(user_name, topic_id):
            section_model = TopicSectionModel(section_heading)

            result = topic_collection.add_section(topic_id, section_model)
            if result is None:
                return {"error" : "DB error"}, 500

            return {"message":"new section added"}

        return {"error" : "Unauthorized action"}, 401
    
    @marshal_with(mfields)
    @protector.protected_by_token
    def patch(self, user_name):
        args = section_parser.parse_args()
        topic_id, section_heading, section_idx = args['topic_id'], args['section_heading'], args['section_idx']

        if topic_collection.get_len_section(topic_id) - 1 < section_idx:
            return {"error" : "section idx not exist"}
        
        if helper_check_ownership(user_name, topic_id):
            
            result = topic_collection.update_section_heading(topic_id, section_idx, section_heading)
            if result is None:
                return {"error" : "DB error"}, 500
            return {"message":"section updated"}

        return {"error" : "Unauthorized action"}, 401


    @marshal_with(mfields)
    @protector.protected_by_token
    def delete(self, user_name):
        args = section_parser.parse_args()
        topic_id, section_idx = args['topic_id'], args['section_idx']

        if topic_collection.get_len_section(topic_id) - 1 < section_idx:
            return {"error" : "section idx not exist"}

        # delete in array
        if helper_check_ownership(user_name, topic_id):
            result = topic_collection.del_section(topic_id, section_idx)
            if result:
                return {"message":"section deleted"}
            return {"error" : "DB error"}, 500
        return {"error" : "Unauthorized action"}, 401
