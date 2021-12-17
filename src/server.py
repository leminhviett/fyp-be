from flask import Flask
from flask_restful import Api       

app = Flask(__name__)
app.config["SECRET_KEY"] = "12345"

api = Api(app)

# only import other module after this line
# otherwise, error can be occured as app & api might be used in these file