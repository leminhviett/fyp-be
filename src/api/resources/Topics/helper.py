from src.api.models import topic_collection
from flask import request
from functools import wraps

def helper_check_ownership(user_name, topic_id):
    result = topic_collection.get_topic(topic_id) 
    return result is not None and result['author_name'] == user_name


def helper_check_is_published(func):
    @wraps(func)
    def wrapper(*args, **kargs):
        try:
            topic_id = request.get_json()['topic_id']
        except Exception as e:
            return {"error" : e}, 500

        result = topic_collection.get_topic(topic_id)

        if (result is None): return {"error" : "DB error"}, 500
        if not result['published']: return func(*args, **kargs)

        return {"error" : "topic is not editable as it is already published"}, 401

    return wrapper