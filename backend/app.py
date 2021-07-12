from filecmp import cmp
from qcloud_cos import CosS3Client

from flask import Flask, request, jsonify, g, json, make_response, render_template
from flask_cors import CORS
from flask_sqlalchemy import func, and_
from ext import db
from private_config import Config
from private_config import BucketConfig
import base64
from model import *
import os
from flask_httpauth import HTTPBasicAuth
from datetime import datetime


def upload_to_bucket(client, bucket, path, file_name):
    response = client.put_object_from_local_file(
        Bucket=bucket,
        LocalFilePath=path,
        Key=file_name,
    )
    print(response['ETag'])
    if os.path.exists(path):
        os.remove(path)


def get_file_url(client, bucket, file_name):
    response = client.get_presigned_download_url(
        Bucket=bucket,
        Key=file_name,
        Expired=3000
    )
    return response
    # pass

pymysql.install_as_MySQLdb()

app = Flask(__name__)
db.init_app(app)
#设置连接数据库的URL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@127.0.0.1:3306/flask_test'

#设置每次请求结束后会自动提交数据库中的改动
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

@app.route('/',endpoint='index')
def index():
    return render_template('index.html')


'''
Api to login
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
        email = request.json.get("email")
        if username is None or password is None:
            return '用户名或密码不能为空'
        if Users.query.filter_by(username=username).first():
            return '用户名重复'
        if password == repassword:
            user = Users(username,password)
            user.hash_password(password)
            db.session.add(user)
            db.session.commit()
            return json.jsonify({'code':200,'msg':'注册成功'})
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

@auth.verify_password
def verify_password(username_or_token, password):
    if request.path == '/api/v1/login':
        user = Users.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    else:
        user = Users.verify_token(username_or_token)
        if not user:
            return False
    g.user = user
    return True


@app.route('/api/v1/login', methods=['GET', 'POST'])
@AuthorizationMixin.login_required
def get_token():
    user = {}
    token = g.user.generate_auth_token()
    user['following'] = resolve_following_relation(g.user.relation)
    user['username'] = g.user.username
    user['uid'] = g.user.uid
    user['brief'] = g.user.brief
    user['email'] = g.user.email
    user['avatar'] = get_file_url(avatar_client, Config.avatar_bucket, g.user.avatar)
    user['phone'] = g.user.phone
    user['sex'] = g.user.sex
    return jsonify({'token': token.decode('ascii'), 'user': user})


def resolve_following_relation(relations):
    rt_relations = {}
    for relation in relations:
        relation = relation.to_json()
        rt_relations[relation['vid']] = relation['status']
    print(rt_relations)
    return rt_relations

if __name__ == '__main__':
    app.run(debug=True)