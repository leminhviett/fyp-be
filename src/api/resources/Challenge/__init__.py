from src.api.models import ChallengeCollection

def helper_check_ownership(user_name, topic_id):
    result = ChallengeCollection.get_challenge_by_id(topic_id)
    if result:
        if result['author_name'] == user_name:
            return True
    
    return False