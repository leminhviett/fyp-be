import logging, os
logging.basicConfig(level=logging.DEBUG)


from src.api.models import *
from dotenv import load_dotenv
from src.server import app

load_dotenv()


if __name__ == "__main__":
    port = 5000
    
    from src.api.models import db_init
    from src.api import routes

    app.run(debug=True, port=port)
