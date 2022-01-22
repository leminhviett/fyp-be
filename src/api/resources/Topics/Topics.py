from email import header
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
    @staticmethod
    def hide_ans(topic):
        for section in topic["sections"]:
            for task in section["tasks"]:
                task["ans"] = "*"*len(task["ans"])
        return topic

    @marshal_with(mfields)
    def get(self, page_num, limit=2):
        if page_num==0: return {"error" : "page_num > 0"}
        # todo: hide ans before sending back to client
        res = topic_collection.get_topics(int(page_num), limit)

        return_res = []
        for topic in res:
            return_res.append(Topics.hide_ans(topic))
        
        return {"payload" : jsonize_cursor(return_res)}

class TopicResource(Resource):
    @staticmethod
    def gen_img_fn(topic_name):
        return f"{topic_name}_{uuid.uuid4()}.png"

    # TODO: only find published topic
    @marshal_with(mfields)
    def get(self):
        user_name = None
        if "bearer_token" in request.headers:
            data = jwt.decode(request.headers["bearer_token"], os.getenv("SECRET_KEY"),algorithms=["HS256"])
            user_name = data["user_name"]

        args = write_parser.parse_args()
        topic_id = str(args['topic_id'])

        res = topic_collection.get_topic(topic_id)
        if res is None: return {"error" : "not found"}
        res['_id'] = str(res['_id'])

        print(user_name, res["author_name"])
        
        if user_name != res["author_name"]:
            for section in res["sections"]:
                for task in section["tasks"]:
                    task["ans"] = "*"*len(task["ans"])

        return {"payload" : res}
    
    # upload an empty topisc
    @marshal_with(mfields)
    @protected_by_token
    def post(self, user_name):
        args = create_parser.parse_args()
        topic_name, topic_desc, banner_img = args['topic_name'], args['topic_desc'], args['banner_img']
        try:
            banner_img_obj = ImgEncoded(banner_img, TopicResource.gen_img_fn(topic_name))
            banner_img_obj.save()
        except Exception as e:
            return {"error" : "img wrong format"}

        try:
            with client.start_session() as session:
                with session.start_transaction():
                    result = topic_collection.insert_topic(
                                    TopicModel(
                                        user_name, 
                                        topic_name,
                                        topic_desc, 
                                        os.path.join(banner_img_obj.sub_folder, banner_img_obj.file_name
                                    )))
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
                    ImgEncoded('', '').delete(f)
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
    