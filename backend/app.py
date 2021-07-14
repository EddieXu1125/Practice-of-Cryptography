from filecmp import cmp
#from forms.main import CommentForm, DescriptionForm
from forms import *
from werkzeug.wrappers import AuthorizationMixin
from werkzeug.utils import redirect, secure_filename
from qcloud_cos import CosS3Client
import pymysql
from flask_login import LoginManager, login_required, login_user, logout_user,current_user
from flask import Flask, request, url_for,flash,jsonify, g, json, make_response, render_template,Blueprint
from flask_cors import CORS
from ext import db
from config import BaseConfig
import base64
from model import *
import os
from flask_httpauth import HTTPBasicAuth

pymysql.install_as_MySQLdb()

app = Flask(__name__)

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
login_manger.login_view='login'
login_manger.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')

#用户注册
@app.route('/register',methods=['POST','GET'])
def register():
    if request.method=='POST':
        name = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        em = request.form.get('email')
        if name is None or password is None:
            return '用户名或密码不能为空'
        if Users.query.filter_by(username=name).first():
            return '用户名重复'
        if password == repassword:
            user = Users(name,password,em)
            user.hash_password(password)
            db.session.add(user)
            db.session.commit()
            return '注册成功'
        else:
            return '两次密码不一致'
    return render_template('Login/register.html')

#用户登录验证
@login_manger.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        form = LoginForm()
        return render_template('Login/login.html', form=form)
    else:
        form = LoginForm(request.form)
        if form.validate():
            username = request.form['username']
            pwd = request.form['password']
            user = Users.query.filter_by(username=username).first()
            if user and user.verify_password(pwd):
                login_user(user)
                return 'login ok'
            else:
                return '密码或用户名错误'
        else:
            print(form.errors)
        return render_template('Login/login.html',form=form)
 
#用户登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('/'))
#允许上传的图片文件   
ALLOWED_EXTENSIONS = {'png','bmp','tiff','jpeg','jpg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#图片上传
@app.route('/upload',methods=['GET','POST'])
@login_required
def upload():
    db.create_all()
    if request.method == 'POST':
        f = request.files['file']
        if allowed_file(f.filename):
            basepath = os.path.dirname(__file__)
            upload_path = os.path.join(basepath,'static/uploads',secure_filename(f.filename))
            f.save(upload_path)
            filename = f.filename
            dis = request.form['discribe']
            photo = Photo(upload_path,dis,current_user._get_current_object())
            db.session.add(photo)
            db.session.commit()
            return '上传成功'
        flash('图片格式违法')
    return render_template('User/upload.html')
    
#展示主页图片
@app.route('/')
def report_photo():
    ROW_PER_PAGE = 5
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['PHOTO_PER_PAGE']
    paginate=Photo.query.order_by(Photo.timestamp.desc()).paginate(page,per_page,error_out=False)
    return render_template('index.html',paginate=paginate,notes=paginate.items)

#展示具体图片
@app.route('/photo/<int:photo_id>')
def show_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['PHOTO_PER_PAGE']
    pagination = Photo.query.with_parent(photo).order_by(Photo.timestamp.asc()).paginate(page, per_page)

    return render_template('main/photo.html', photo=photo)


#点赞图片
@app.route('/photo/<int:photo_id>')
@login_required
def like_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo:
        photo.like += 1
        db.session.commit()
        flash('Like Photo','success')
    else:
        flash('No photo')
    return redirect(url_for('show_photo',photo_id=photo.id))


if __name__ == '__main__':
    app.run(debug=True)