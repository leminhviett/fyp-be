from src.server import api
from src.api.resources import *

api.add_resource(AuthUser, "/auth", "/register")
api.add_resource(Topics, "/topics")
api.add_resource(Topic, "/topic")
api.add_resource(SectionTopic, "/topic/section")
api.add_resource(TaskTopic, "/topic/task")


# api.add_resource(Challenge, "/challenge")
# api.add_resource(TaskChallenge, "/challenge/task")