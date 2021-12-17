from src.server import api
from src.api.resources import *

api.add_resource(AuthUser, "/auth", "/register")
api.add_resource(Topics, "/topics")
api.add_resource(Topic, "/topic")
api.add_resource(Task, "/topic/task")

