from forms import *
from werkzeug.wrappers import AuthorizationMixin
from werkzeug.utils import redirect, secure_filename
import pymysql
from ext import db
from flask_login import LoginManager, login_required, login_user, logout_user,current_user,login_manager
from flask import Flask, request, url_for,flash,jsonify, g, json, make_response, render_template,Blueprint
from config import BaseConfig
from model import *
import os
from flask_httpauth import HTTPBasicAuth
from flask_bootstrap import Bootstrap

pymysql.install_as_MySQLdb()
DB_NAME='database.db'
app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@127.0.0.1:3306/flask_test'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD'] = 'upload'
db.init_app(app)


login=LoginManager()
login.init_app(app)
login.session_protection='strong'
login.login_view='login'

#用户注册
@app.route('/register',methods=['POST','GET'])
def register():
    db.create_all()
    if request.method=='POST':
        name = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        em = request.form.get('email')
        if name is None or password is None:
            flash('Username or Password can\'t empty')
            return render_template('Login/register.html')

        elif len(name) < 5:
             flash('Username can\'t less than 5')
             return render_template('Login/register.html')

        elif Users.query.filter_by(username=name).first():
            flash('Username is used')
            return render_template('Login/register.html')

        elif len(password) < 6:
            flash('Password can\'t less than 6')
            return render_template('Login/register.html')

        if password == repassword:
            user = Users(name,password,em)
            user.hash_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user,remember=True)
            flash('Register successfully')
            return redirect(url_for('index'))

        else:
            flash('Password must be same')
            return render_template('Login/register.html')

    return render_template('Login/register.html')


@login.user_loader
def user_loader(user_id):
  user =Users.query.filter_by(id=user_id).first()
  if user is not None:
     return user
  else:
     return None

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
                login_user(user,remember=True)
                flash('login ok')
                return redirect(url_for('home'))
            else:
                flash('Password or Username error')
                return render_template('Login/login.html',form=form)
        else:
            print(form.errors)
            flash('Login Failed')
            return render_template('Login/login.html',form=form)


#用户登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#允许上传的图片文件   
ALLOWED_EXTENSIONS = {'png','bmp','tiff','jpeg','jpg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#图片上传
@app.route('/upload',methods=['GET','POST'])
@login_required
def upload():
    if request.method == 'POST':
        f = request.files['files']
        discription = request.form.get('data')
        if allowed_file(f.filename):
            basepath = os.path.dirname(__file__)
            upload_path = os.path.join(basepath,'static/uploads',secure_filename(f.filename))
            filename = f.filename
            photo = Photo(filename,upload_path,discription,current_user.get_id())
            db.session.add(photo)
            db.session.commit()
            f.save(upload_path)
            flash('Upload Successfully')
            return redirect(url_for('show_photo',photo_id=photo.id))
        else:
            flash('Photo Extension error!')
            return redirect(url_for('upload'))
    else:
        return render_template('User/upload.html')

@app.route('/')
def index():
    db.create_all()
    ROWS_PER_PAGE = 5
    page = int(request.args.get('page', 1)) 
    per_page = int(request.args.get('per_page', 5))
    paginate=Photo.query.order_by(Photo.timestamp.desc()).paginate(page,per_page,error_out=False)
    return render_template('index.html',user=current_user,paginate=paginate,photos=paginate.items)


#展示具体图片
@app.route('/photo/<int:photo_id>')
def show_photo(photo_id):
     photo = Photo.query.get_or_404(photo_id)
     return render_template('User/photo.html', photo=photo)

@app.route('/delete-note',methods=['POST'])
def delete_note():
    photo=json.loads(request.data)
    photoId= photo['noteId']
    photo=Photo.query.get(photoId)
    if photo:
        if photo.author_id==current_user.id:
            db.session.delete(photo)
            db.session.commit()
            os.remove(os.path.join(photo.filepath))
    return redirect(url_for('home'))

@app.route('/like-note',methods=['POST'])
@login_required
def like_note():
    photo=json.loads(request.data)
    photoId=photo['noteId']
    photo=Photo.query.get(photoId)
    if photo:
        if photo.like == None:
            photo.like = 1
        else:
            photo.like +=1
        db.session.commit()
    return jsonify({})

@app.route('/home',methods=['GET','POST'])
@login_required
def home():
    ROWS_PER_PAGE = 5
    page = int(request.args.get('page', 1)) 
    per_page = int(request.args.get('per_page', 5))
    paginate=Photo.query.filter_by(author_id=current_user.id).order_by(Photo.timestamp.desc()).paginate(page,per_page,error_out=False)
    return render_template("User/home.html",user=current_user,paginate=paginate)

@app.route('/u/<int:user_id>',methods=['POST','GET'])
def other(user_id):
    user = Users.query.get(user_id)
    if user:
        ROWS_PER_PAGE = 5
        page = int(request.args.get('page', 1)) 
        per_page = int(request.args.get('per_page', 5))
        paginate=Photo.query.filter_by(author_id=user.id).order_by(Photo.timestamp.desc()).paginate(page,per_page,error_out=False)
        return render_template('User/other.html',user=user,visitor=current_user,paginate=paginate)


if __name__ =="__main__":
  app.run(host='0.0.0.0',port=80,debug=True)
