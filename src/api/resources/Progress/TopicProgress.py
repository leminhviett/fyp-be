
# user learn a topic: => POST then create a new topic progress resource, username extracted from his token
# user finish a task in topic => PATCH
# user unenroll from a topic => DELETE

from flask_restful import Resource, marshal_with, reqparse
from src.api.models import *
from src.api.middlewares.protector import protected_by_token
from src.utils.utils import get_response_format

topic_prog_parser = reqparse.RequestParser()
topic_prog_parser.add_argument("topic_id", type=str, help="topic id is reuqired", required=True)
topic_prog_parser.add_argument("section_idx", type=int)
topic_prog_parser.add_argument("task_idx", type=int)
topic_prog_parser.add_argument("task_ans", type=str)


mfields = get_response_format()

class TopicProgress(Resource):

    @marshal_with(mfields)
    @protected_by_token
    def get(self, user_name):
        return {"payload" :  jsonize_cursor(topic_prog_collection.get_progresses(user_name))}


    @marshal_with(mfields)
    @protected_by_token
    def post(self, user_name):
        args = topic_prog_parser.parse_args()
        topic_id = args['topic_id']

        find_topic = topic_collection.get_topic(str(topic_id))
        if find_topic is None or not find_topic['published']: return {"error" : "topic not found"}

        find_progress = topic_prog_collection.get_progess(topic_id, user_name)
        if find_progress: return {"error" : "duplicate progress found"}, 400

        new_progress = TopicProgressModel(topic_id, user_name)
        result = topic_prog_collection.add_progress(new_progress)

        if result:
            return {"message" : "progress added"}
        return {"error" : "DB error"}, 500
    
    @marshal_with(mfields)
    @protected_by_token
    def delete(self, user_name):
        args = topic_prog_parser.parse_args()
        topic_id = args['topic_id']

        result = topic_prog_collection.del_progress(topic_id, user_name)

        if result:
            return {"message" : "progress deleted"}
        return {"error" : "topic not found"}, 400

    @marshal_with(mfields)
    @protected_by_token
    def patch(self, user_name):
        args = topic_prog_parser.parse_args()
        topic_id, section_idx, task_idx, task_ans = args['topic_id'], args['section_idx'], args['task_idx'], args['task_ans']

        find_topic = topic_collection.get_topic(str(topic_id))
        if find_topic is None or not find_topic['published']: return {"error" : "topic not found"}
        
        try:
            if find_topic['sections'][section_idx]['tasks'][task_idx]['ans'] != task_ans:
                return {"error" : "ans submited is wrong"}
        except Exception as e:
            return {"error" : f"invalid data submitted; {e}"}, 401

        result = topic_prog_collection.update_progress(topic_id, user_name, section_idx, task_idx)

        if result:
            return {"message" : "progress updated"}
        return {"error" : "DB error"}, 500
