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
    SECRET_KEY = 'Luminous'
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024 