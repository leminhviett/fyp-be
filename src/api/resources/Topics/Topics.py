from flask_restful import Resource, marshal_with, reqparse
from src.api.models import *
from src.api.middlewares.protector import protected_by_token
from src.utils.utils import get_response_format
from src.utils.storage import ImgEncoded
from .helper import *
import uuid

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
        # todo: hide ans before sending back to client
        res = topic_collection.get_topics()
        for ele in res:
            print(ele)
        return {"payload" : jsonize_cursor(res)}

class TopicResource(Resource):
    @staticmethod
    def gen_img_fn(topic_name):
        return f"{topic_name}-{uuid.uuid4()}.png"

    # TODO: only find published topic
    @marshal_with(mfields)
    def get(self):
        return {"payload" : topic_collection.get_topic(id)}
    
    # upload an empty topisc
    @marshal_with(mfields)
    @protected_by_token
    def post(self, user_name):
        args = create_parser.parse_args()
        topic_name, topic_desc, banner_img = args['topic_name'], args['topic_desc'], args['banner_img']

        banner_img_obj = ImgEncoded(banner_img.encode(), TopicResource.gen_img_fn(topic_name))
        banner_img_obj.save()

        try:
            with client.start_session() as session:
                with session.start_transaction():
                    result = topic_collection.insert_topic(TopicModel(user_name, topic_name, topic_desc, banner_img_obj.full_loc))
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
            target_topic = topic_collection.get_topic(topic_id)
            if target_topic is None:
                return {"message" : "topic id not found"}
            
            removed_files = [target_topic['banner_img']]

            for section in target_topic['sections']:
                for task in section['tasks']:
                    removed_files.append(task['img_loc'])

            for f in removed_files:
                try:
                    os.remove(f)
                except OSError:
                    pass

            try:
                with client.start_session() as session:
                    with session.start_transaction():
                        topic_collection.del_topic(topic_id)
                        user_collection.del_topic(user_name, topic_id)
                return {"message" : "deleted topic successfully"}
            except Exception as e:
                return {"error" : e}, 500

        return {"error" : "Unauthorized action"}, 401

    @marshal_with(mfields)
    @protected_by_token
    def patch(self, user_name):
        args = write_parser.parse_args()
        topic_id = str(args['topic_id'])

        if helper_check_ownership(user_name, topic_id):
            # set topic to be published
            result = topic_collection.set_topic_published(topic_id)
            if result is None: return {"error" : "DB error"}, 500
            
            return {"message" : "successfully done"}

        return {"error" : "Unauthorized action"}, 401
        