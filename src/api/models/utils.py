from pymongo import MongoClient
from src.server import app
import functools

def db_conn(host, port=27017):
    try:
        client = MongoClient(host=host, port=port)
        db = client.cyber_expert
        app.logger.info("[SUCCESS] DB Connected")
        return db, client
    except Exception as e:
        app.logger.error("[ERROR] DB cannot be reached")
        quit()

def db_err_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kargs):
        try:
            return func(*args, **kargs)
        except Exception as e:
            app.logger.error(f"DB error: {e}")
            
    return wrapper

from bson.json_util import dumps

def jsonize_cursor(cursor):
    return dumps(list(cursor))