from src.api.models import topic_collection

def helper_check_ownership(user_name, topic_id):
    result = topic_collection.get_topic_by_id(topic_id)
    if result:
        if result['author_name'] == user_name:
            return True
    
    return False