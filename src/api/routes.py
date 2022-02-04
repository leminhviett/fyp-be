from src.api.resources.AuthUser import UserDev
from src.server import api
from src.api.resources import *

api.add_resource(AuthUser, "/auth", "/register")
api.add_resource(UserDev, "/my_dev")

api.add_resource(Topics, "/topics/<page_num>")
api.add_resource(Challenges, "/challenges/<page_num>")

api.add_resource(TopicResource, "/topic")
api.add_resource(SectionTopic, "/topic/section")
api.add_resource(TaskTopic, "/topic/task")

api.add_resource(ChallengeResource, "/challenge")
api.add_resource(TaskChallenge, "/challenge/task")

api.add_resource(TopicProgress, "/progress/topic")
api.add_resource(EachTopicProgress, "/progress/topic/<topic_id>")

api.add_resource(UserContainer, "/user_container")
api.add_resource(SQLInj, "/sql_inj")

