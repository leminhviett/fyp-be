from datetime import datetime, timedelta
import jwt, os
 
class TokenModel:
    '''
        JWT token
        only 1 valid JWT token for each user at any time
    '''
    LONG_TTL = timedelta(days=1)
    START_POINT = datetime(1970,1,1)

    def __init__(self, user_name):
        self.user_name = user_name
        self.exp = int((datetime.utcnow() + self.LONG_TTL - self.START_POINT).total_seconds())
        self.digest = jwt.encode({"user_name" : user_name, "exp" : self.exp}, os.getenv("SECRET_KEY"),algorithm="HS256")
    
    @classmethod
    def valid(cls, exp:int):
        return exp > int((datetime.utcnow() - cls.START_POINT).total_seconds())

    @classmethod
    def get_latest_exp(cls ):
        return int((datetime.utcnow() + cls.LONG_TTL - cls.START_POINT).total_seconds())
