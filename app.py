from flask import Flask, render_template, request, redirect
# DB操作モジュール
from flask_sqlalchemy import SQLAlchemy
# flaskapp内でログイン操作で利用するモジュール。
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from datetime import datetime
# タイムゾーンを正しく扱うためのモジュール。
import pytz
# randompassword作成のため。
import os
# hash passwpord生成と確認用のモジュールをインストール
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blog.db'
# SECRETKEYとは、唯一無二の鍵。それ以降はわからん。
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
boostrap = Bootstrap(app)

# flaskでログインするための部品。この部品とアプリを接続する。
login_manager = LoginManager()
login_manager.init_app(app)

# 各DBクラスを作成。
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone("Asia/Tokyo")))
    
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

# @login_manager.user_loader: Session中のUser情報をDBから取得する。
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# GET、POSTの使い分けはもう少し作りながら理解する必要あり。
@app.route('/', methods=["GET", "POST"])
#login_requiredは、ログインをしていいない場合、起動することはできない。めっちゃ便利！！
@login_required
def index():
    if request.method == "GET":
        posts = Post.query.all()
        return render_template("index.html", posts=posts)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    # POSTの場合
    if request.method == "POST":
        title = request.form.get("title")
        body = request.form.get("body")
        post = Post(title=title, body=body)
        db.session.add(post)
        db.session.commit()
        return redirect("/")
    # GETの場合
    else:
        return render_template("create.html")

# たまに画面が崩れる。何か処理上で問題ありか。
@app.route("/<int:id>/update", methods=["GET", "POST"])
@login_required
def update(id):
    # Postを更新するときは、idをDBから取得して、内容を更新させる。
    post = Post.query.get(id)
    # GETの場合
    if request.method == "GET":
        return render_template("update.html", post=post)
    # POSTの場合
    else:
        post.title = request.form.get("title")
        post.body = request.form.get("body")
        db.session.commit()
        return redirect("/")


@app.route("/<int:id>/delete", methods=["GET"])
@login_required
def delete(id):
    # Postを更新するときは、idをDBから取得して、内容を更新させる。
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect("/")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    # POSTの場合
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # hashとは：元のデータを不規則な文字列に置き換える処理。不可逆性があり、元のパスワードを入手するのは困難。
        user = User(username=username, password=generate_password_hash(password, method="sha256"))
        # 新規でUserを追加するときは、addメソッドでDBに情報を追加する。
        db.session.add(user)
        # DBに変更を与えるときは、commitを忘れず。
        db.session.commit()
        return redirect("/login")
    # GETの場合
    else:
        return render_template("signup.html")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    # POSTの場合
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect("/")
    # GETの場合
    else:
        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    # ログアウトメソッドを実行するだけ。簡単。
    logout_user()
    return redirect("/login")

    # app.pyで起動できるようにする
if __name__ == "__main__":
    app.run()
