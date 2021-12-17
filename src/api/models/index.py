from src.api.models import *

cyber_expert_db, client = utils.db_conn("localhost")
user_collection = UserCollection(cyber_expert_db)
topic_collection = TopicCollection(cyber_expert_db)
