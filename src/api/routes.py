from src.server import api
from src.api.resources import *

api.add_resource(AuthUser, "/auth", "/register")
api.add_resource(Topics, "/topics")

api.add_resource(TopicResource, "/topic")
api.add_resource(SectionTopic, "/topic/section")
api.add_resource(TaskTopic, "/topic/task")

api.add_resource(ChallengeResource, "/challenge")
api.add_resource(TaskChallenge, "/challenge/task")

api.add_resource(TopicProgress, "/progress/topic")
