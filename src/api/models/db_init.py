from .utils import db_conn
from .User import UserCollection
from .Topic import TopicCollection
from .Challenge import ChallengeCollection

db_inst, client = db_conn("localhost")
user_collection = UserCollection(db_inst)
topic_collection = TopicCollection(db_inst)
challenge_collection = ChallengeCollection(db_inst)
