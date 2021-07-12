from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context
from ext import db
from private_config import Config
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature

class Role(db.Model):
    # 定义表名
    __tablename__ = 'roles'
    # 定义列对象
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    us = db.relationship('User', backref='role')
 
 
class Users(db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(64))
    email = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    admire = db.Column(db.String(4096), default=None)
    brief = db.Column(db.String(200))
    relation = db.relationship('Relation', order_by='Relation.id', backref='user')

    def __init__(self, username, password,email):
        self.name = username
        self.password = password
        self.email = email

    def hash_password(self, password):
        self.password = custom_app_context.encrypt(password)

    def verify_password(self, password):
        return custom_app_context.verify(password, self.password)
 
    def generate_auth_token(self, expiration = 600):
        s = Serializer(Config.SECRET_KEY, expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(Config.SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = Users.query.get(data['uid'])
        return user



class Resource(db.Model):
    __tablename__ = 'timeline'
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer)
    img = db.Column(db.String(200))
    desc = db.Column(db.String(100))
    author = db.Column(db.String(30))
    date = db.Column(db.DateTime)

    def __init__(self, uid, img, desc, author, date):
        self.uid = uid
        self.img = img
        self.desc = desc
        self.author = author
        self.date = date

class Comments(db.Model):
    __tablename__ = 'comments'
    cid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pid = db.Column(db.Integer, nullable=False)
    uid = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.String(1024))
    username = db.Column(db.String(80))
    datetime = db.Column(db.DateTime)

    def __init__(self, pid, uid, comments, username, datetime):
        self.pid = pid
        self.uid = uid
        self.comments = comments
        self.username = username
        self.datetime = datetime

class Relation(db.Model):
    __tablename__ = 'relation'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer, ForeignKey('users.uid'))
    vid = db.Column(db.Integer)
    status = db.Column(db.Boolean)

    def __init__(self, uid, vid, status):
        self.uid = uid
        self.vid = vid
        self.status = status

# m_type:
# 1 admire messages
# 2 comment messages
# 3 follow messages
# 4 forward messages
class Message(db.Model):
    __tablename__ = 'message'
    mid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer, nullable=False)
    vid = db.Column(db.Integer, nullable=False)
    pid = db.Column(db.Integer)
    m_type = db.Column(db.Integer, nullable=False)
    m_content = db.Column(db.String(100))
    m_status = db.Column(db.Boolean, default=True)

    def __init__(self, uid, vid, pid, m_type, m_content, m_status):
        self.uid = uid
        self.vid = vid
        self.pid = pid
        self.m_type = m_type
        self.m_content = m_content
        self.m_status = m_status
