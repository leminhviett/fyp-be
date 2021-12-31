from src.api.models import challenge_collection

def helper_check_ownership(user_name, topic_id):
    result = challenge_collection.get_challenge(topic_id)
    if result:
        if result['author_name'] == user_name:
            return True
    
    return False