import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from dotenv import load_dotenv
load_dotenv()



ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']   # should be kept secret
JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY']    # should be kept secret


def create_access_token(data: dict):
    to_encode = data.copy()

    # expire time of the token
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

    # return the generated token
    return encoded_jwt