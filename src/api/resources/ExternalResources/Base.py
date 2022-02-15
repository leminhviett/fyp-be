from flask_restful import Resource, marshal_with
from src.utils.utils import get_response_format

mfields = get_response_format()


class BaseResource(Resource):
    EXT_SERVICE = "http://localhost:8000"

    @marshal_with(mfields)
    def post(self):
        pass
    
    @marshal_with(mfields)
    def delete(self):
        pass

