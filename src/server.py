from flask import Flask, send_from_directory
from flask_restful import Api       
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__, static_url_path='', static_folder='../storage')
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
CORS(app)

api = Api(app)

# serve static file
@app.route('/<path>')
def send_storage(path):
    if path is None:
        return {"error" : "file not found"}
    return send_from_directory(path)

# only import other module after this line
# otherwise, error can be occured as app & api might be used in these file
