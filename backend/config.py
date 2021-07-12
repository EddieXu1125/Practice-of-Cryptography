DEBUG = True
SQLALCHEMY_ECHO = False
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/flask_test'
SECRET_KEY = '*\xff\x93\xc8w\x13\x0e@3\xd6\x82\x0f\x84\x18\xe7\xd9\\|\x04e\xb9(\xfd\xc3'
common/_init_.py
# config=utf-8 
from flask_sqlalchemy import SQLAlchemy 

__all__ = ['db'] 
db = SQLAlchemy()