from filecmp import cmp
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
from forms import *
import os
from flask_httpauth import HTTPBasicAuth
from flask_bootstrap import Bootstrap

pymysql.install_as_MySQLdb()

app = Flask(__name__)
bootstrap = Bootstrap(app)

#设置连接数据库的URL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:rl0twsaduk@127.0.0.1:3306/flask_test'
#设置每次请求结束后会自动提交数据库中的改动
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD'] = 'upload'
app.config.from_object(BaseConfig)
db.init_app(app)

# 判断文件夹是否存在，不存在建一个
# upload_dir = os.path.join(
#     app.instance_path, 'upload' 
# )
upload_dir = os.path.join('.','upload')
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir, mode=0o755)


login_manger=LoginManager()
login_manger.session_protection='strong'
login_manger.login_view='login'
login_manger.init_app(app)


@app.route('/')
def index():
    db.create_all()
    ROWS_PER_PAGE = 5
    page = int(request.args.get('page', 1)) 
    per_page = int(request.args.get('per_page', 5))
    paginate=Photo.query.order_by(Photo.timestamp.desc()).paginate(page,per_page,error_out=False)
    return render_template('index.html',user=current_user,paginate=paginate,notes=paginate.items)



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
            flash('注册成功')
            return redirect(url_for('index'))
        else:
            return '两次密码不一致'
    return render_template('Login/register.html')

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
        if form.validate_on_submit():
            username = request.form['username']
            pwd = request.form['password']
            user = Users.query.filter_by(username=username).first()
            if user and user.verify_password(pwd):
                login_user(user,remember=True)
                flash('Logged in successfully!')
                return redirect(url_for('index')) 
            else:
                flash('Password or Username error')
                return render_template('Login/login.html',form=form)
        else:
            print(form.errors)
            flash('Login Failed')
            return render_template('Login/login.html',form=form,user=current_user)


#用户登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已退出登录')
    return redirect(url_for('index'))

#图片上传

#允许上传的图片文件   
ALLOWED_EXTENSIONS = {'png','bmp','tiff','jpeg','jpg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload',methods=['GET','POST'])
@login_required
def upload():
    if request.method == 'POST':
        f = request.files['file']
        if allowed_file(f.filename):
            upload_path = os.path.join(upload_dir,secure_filename(f.filename))
            f.save(upload_path)
            filename = f.filename
            photo = Photo(filename,upload_path,current_user.get_id())
            db.session.add(photo)
            db.session.commit()
            flash('Upload Successfully')
            return 'Successfully'
            # redirect(url_for('show_photo',photo_id=photo.id))
        else:
            flash('Photo Extension error!')
            redirect(url_for('upload'))
    else:
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

    return render_template('User/home.html', photo=photo)

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
    # db.create_all()
    app.run(host='0.0.0.0',debug=app.config['DEBUG'])