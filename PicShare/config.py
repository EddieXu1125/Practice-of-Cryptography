import os
import sys

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')
