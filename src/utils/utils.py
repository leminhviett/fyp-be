import functools
from src.server import app
from flask_restful import fields
def db_err_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kargs):
        try:
            return func(*args, **kargs)
        except Exception as e:
            app.logger.error(e)
            
    return wrapper

def get_response_format():
    mfields = {'message': fields.String, 'error' : fields.String,'payload' : fields.Raw}
    return mfields