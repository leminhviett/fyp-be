import logging, os

from flask_restful import Resource
# from src.api.resources.TokenProtected.Topics import Topics
from src.api.models import *
from dotenv import load_dotenv
from src.server import app, api

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    port = 5000
    
    from src.api.models import db_init
    from src.api import routes

    app.run(debug=True, port=port)

