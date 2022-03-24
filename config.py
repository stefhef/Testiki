from dotenv import load_dotenv
import os

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM')
SECRET_KEY = os.environ.get('SECRET_KEY')