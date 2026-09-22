import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///barakah.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    from datetime import timedelta
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
