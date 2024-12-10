import flask
import hashlib
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from os import path, makedirs, listdir
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'mp3', 'flac', 'wav', 'aac', 'ogg', 'm4a', 'opus'}
MAX_FILE_SIZE = 35 * 1024 * 1024  # 25 мегабайт

# python -c "import secrets; print(secrets.token_hex(16))" for SECRET_KEY
app.config['SECRET_KEY'] = 'nope'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE


db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    hash = db.Column(db.String(64), nullable=False)

class Songs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    filename = db.Column(db.String(150), nullable=False)


with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if not path.isdir(UPLOAD_FOLDER):
    makedirs(UPLOAD_FOLDER)

def is_allowed_file(filename):
    return True

@app.route('/')
def index():
    return render_template('index.html', user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        if User.query.filter_by(username=username).first():
            flash('пользователь с таким ником уже существует', 'danger')
            return redirect(url_for('register'))
        else:
            new_user = User(username=username, hash=hash)
            db.session.add(new_user)
            db.session.commit()
            flash('успешная деградация! залогиньтесь пжпжжп', 'success')
            return redirect(url_for('login'))
    return render_template('login_n_reg/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        user = User.query.filter_by(username=username).first()
        if user and user.hash == hash:
            login_user(user)
            flask.flash('Успешный логин!')
            return redirect(url_for('index'))
        flash('Неверное имя пользователя или пароль', 'danger')
        return redirect(url_for('index'))
    return render_template('login_n_reg/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('вы успешно вышли из аккаунта', 'success')
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
#@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'Файл не найден', 400

        file = request.files['file']

        if not file.filename:
            return 'Имя файла пустое', 400

        if not file.filename.strip():
            return 'Имя файла пустое', 400

        if file:
            try:
                filename = file.filename
                filepath = path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                flash(f'{filename} загужен!!', 'success')
                new_song = Songs(filename=filename, username=current_user.username)
                db.session.add(new_song)
                db.session.commit()
                return redirect(url_for('upload'))
            except Exception:
                flash('Неподдерживаемый формат либо какая-то ошибка', 'danger')
                return redirect(url_for('upload'))

    return render_template('upload.html', user=current_user)

@app.route('/uploads')
def uploads():
    files = listdir(UPLOAD_FOLDER)
    amount = len(files)
    return render_template('uploads.html', files=files, user=current_user, amount=amount)


if __name__ == '__main__':
    app.run(debug=True,)
