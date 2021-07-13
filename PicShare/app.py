from filecmp import cmp
from werkzeug.wrappers import AuthorizationMixin
from qcloud_cos import CosS3Client
import pymysql
from flask_login import LoginManager, login_required, login_user, logout_user
from flask import Flask, request, url_for,flash,jsonify, g, json, make_response, render_template,Blueprint
from flask_cors import CORS
from ext import db
from config import Config
import base64
from model import *
import os
from flask_httpauth import HTTPBasicAuth
from flask_bootstrap import Bootstrap

pymysql.install_as_MySQLdb()

app = Flask(__name__)
bootstrap = Bootstrap(app)
db.init_app(app)
#设置连接数据库的URL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@127.0.0.1:3306/flask_test'

#设置每次请求结束后会自动提交数据库中的改动
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD'] = 'static/photo'

login_manger=LoginManager()
login_manger.session_protection='strong'
login_manger.login_view='blog.login'
login_manger.init_app(app)


@app.route('/')
def index():
    return render_template('base.html')

'''
Api to sgin in
content:application/json
input:
{
    "username":"username",
    "password":"password"
    "repassword":"repassword"
    "email":"email"
}
'''

@app.route('/register',methods=['POST','GET'])
def register():
    db.create_all()
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        email = request.form.get("email")
        if username is None or password is None:
            return '用户名或密码不能为空'
        # if Users.query.filter_by(username=username).first():
        #     return '用户名重复'
        if password == repassword:
            user = Users(username,password,email)
            user.hash_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('/'))
        else:
            return '两次密码不一致'
    return render_template('register.html')

"""
Api to login
content:application/json
input:
{
    "username":"username",
    "password":"password"
}
output:
{
    'username':username,
    'data':'string tips'
}
"""

@login_manger.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()
        if not user or not user.verify_password(password):
               return "用户名或密码错误"
        return "登录成功"
    else:
        return render_template('login.html')
 
#用户登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已退出登录')
    return redirect(url_for('/'))

if __name__ == '__main__':
    app.run(debug=True)