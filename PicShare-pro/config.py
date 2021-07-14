import os
import sys

class BaseConfig:
    ADMIN_EMAIL = os.getenv('Luminous','admin@helloflask.com')
    PHOTO_PER_PAGE = 12
    COMMENT_PER_PAGE = 15
    NOTIFICATION_PER_PAGE = 20
    USER_PER_PAGE = 20
    SEARCH_RESULT_PER_PAGE = 20
    PHOTO_SIZE =  500
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024 
    SQLALCHEMY_DATABASE_URI = 'mysql://root:rl0twsaduk@127.0.0.1:3306/flask_test'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    DEBUG: True
    ENV: 'development'