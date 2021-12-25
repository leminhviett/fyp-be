from flask_restful import Resource, marshal_with, reqparse
from src.api.models import *
from src.api.middlewares.protector import protected_by_token
from src.utils.utils import get_response_format
from .helper import *

create_parser = reqparse.RequestParser()
create_parser.add_argument("topic_name", type=str, help="topic name is reuqired", required=True)
create_parser.add_argument("topic_desc", type=str, help="topic desc is reuqired", required=True)
create_parser.add_argument("banner_img", type=str)

write_parser = reqparse.RequestParser()
write_parser.add_argument("topic_id", type=str, help="topic id is reuqired", required=True)

mfields = get_response_format()

class Topics(Resource):
    # TODO: pagination needed
    @marshal_with(mfields)
    def get(self):
        return {"payload" : jsonize_cursor(topic_collection.get_topics())}

class Topic(Resource):
    @marshal_with(mfields)
    def get(self):
        return {"payload" : topic_collection.get_topic_by_id(id)}

    # upload an empty topisc
    @marshal_with(mfields)
    @protected_by_token
    def post(self, user_name):
        args = create_parser.parse_args()
        topic_name, topic_desc, banner_img = args['topic_name'], args['topic_desc'], args['banner_img']

        try:
            with client.start_session() as session:
                with session.start_transaction():
                    result = topic_collection.insert_topic(TopicModel(user_name, topic_name, topic_desc, banner_img))
                    result2 = user_collection.push_topic(user_name, str(result.inserted_id))
            if result2:        
                return {"message" : "successfully added topic"}
        except Exception as e:
            return {"error" : e}, 500
    
    @marshal_with(mfields)
    @protected_by_token
    def delete(self, user_name):
        args = write_parser.parse_args()
        topic_id = str(args['topic_id'])

        if helper_check_ownership(user_name, topic_id):
            try:
                with client.start_session() as session:
                    with session.start_transaction():
                        topic_collection.del_topic(topic_id)
                        user_collection.del_topic(user_name, topic_id)
                return {"message" : "deleted topic successfully"}
            except Exception as e:
                return {"error" : e}, 500

        return {"error" : "Unauthorized action"}, 401
   