from src.api.models import challenge_collection
import uuid

def helper_check_ownership(user_name, topic_id):
    result = challenge_collection.get_challenge(topic_id)
    if result:
        if result['author_name'] == user_name:
            return True
    
    return False

def gen_unique_filename(user_name, file_name):
    return f"{user_name}-{uuid.uuid4()}-{file_name}"
