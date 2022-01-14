from flask import Flask
from flask_restful import Api       
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
CORS(app)

api = Api(app)

# only import other module after this line
# otherwise, error can be occured as app & api might be used in these file
