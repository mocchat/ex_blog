from flask import Flask, render_template, request, session, flash, g, redirect, url_for, send_from_directory
from datetime import date, datetime
import smtplib
import hashlib
import pymysql
import json
from flask_ckeditor import CKEditor
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship  # 댓글 모델과 연관 관계 설정을 위해 추가

app = Flask(__name__)
ckeditor = CKEditor(app)
OWN_EMAIL = "5658love5658@gmail.com"
OWN_PASSWORD = "svikaanwyilxmwdh"
app.config["SECRET_KEY"] = "ABCD"

# 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:!aa47287846@localhost/blog_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    subtitle = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    comments = relationship('Comment', backref='post', lazy=True)

# 댓글 작성 라우트
@app.route('/add_comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    if request.method == 'POST':
        if g.user is not None:  # 사용자가 로그인한 경우에만 댓글 작성을 허용합니다
            user_id = g.user
            content = request.form.get('comment_text')
            comment = Comment(post_id=post_id, user_id=user_id, content=content)
            db.session.add(comment)
            db.session.commit()
        else:
            flash("로그인이 필요합니다.")  # 사용자가 로그인하지 않은 경우 메시지를 표시합니다.
    return redirect(url_for('post', post_id=post_id))


# 포스트 페이지에서 댓글 표시
@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).all()
    return render_template('post.html', post=post, comments=comments)


@app.route('/')
@app.route('/home',)
def home():
    return render_template("index.html", year=year)


#따로 라우팅하지 않은 page 경로 (ex/ sample.html)
@app.route('/<string:page>')
def page(page: str):
    return render_template(page, year=year)


@app.route('/sample')
def sample():
    return render_template("sample.html", year=year)


@app.route('/about')
def about():
    return render_template("about.html", year=year)


#favicon 관련 오류 해결
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/v[nd.microsoft.icon')


#각 포스트 페이지 
@app.route("/post/<int:index>/<category>")
def show_post(index, category):
    requested_post = None
    posts = []
    if category == 'Blog':
        f = open('./static/json/post.json', 'r')
        posts = json.load(f)
        f.close()
    elif category == 'Test':
        f = open('./static/json/Test.json', 'r')
        posts = json.load(f)
        f.close()
    elif category == 'Algo':
        f = open('./static/json/algo.json', 'r')
        posts = json.load(f)
        f.close()
    for blog_post in posts:
        if blog_post["id"] == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


#컨택
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        data = request.form
        send_email(data["name"], data["email"], data["phone"], data["message"])
        return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", msg_sent=False)


#로그인 비번은 qwer
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        error = None
        password = request.form['password']
        m = hashlib.sha256()
        m.update(password.encode('utf-8'))  #f6f2ea8f45d8a057c9566a33f99474da2e5c6a6604d736121650e2730c6fb0a3 (비번은 'qwer')
        if m.hexdigest() != 'f6f2ea8f45d8a057c9566a33f99474da2e5c6a6604d736121650e2730c6fb0a3' and m.hexdigest() != '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4':
            error = "비밀번호가 올바르지 않습니다."
        if error is None:
            session.clear()
            if password == 'qwer':
                session['manager'] = 'mocchat'
            else:
                session['manager'] = 'lindin'
            return redirect(url_for('home'))
        flash(error)
    return render_template("login.html")


#블로그 포스팅 보는 곳
@app.route("/blog_post", methods=["GET", "POST"])
def blog_post():
    f = open('./static/json/post.json', 'r')
    posts = json.load(f)
    f.close()
    if request.method == "POST":
        if request.form['check'] == 'del':
            pid = int(request.form['id'])
            for i in range(len(posts)):
                if posts[i]['id'] == pid:
                    del posts[i]
                    break
            f = open('./static/json/post.json', 'w')
            json.dump(posts, f, indent="\t")
            f.close()
            return redirect(url_for('blog_post'))
        if request.form['check'] == 'edit':
            pid = int(request.form['id'])
            for i in range(len(posts)):
                if posts[i]['id'] == pid:
                    f.close()
                    return render_template("edit.html", epost=posts[i])
    return render_template("blog_post.html", year=year, all_posts=posts)


#테스트 포스팅 보는곳 
@app.route("/test_post", methods=["GET", "POST"])
def test_post():
    f = open('./static/json/test.json', 'r')
    posts = json.load(f)
    f.close()
    if request.method == "POST":
        if request.form['check'] == 'del':
            pid = int(request.form['id'])
            for i in range(len(posts)):
                if posts[i]['id'] == pid:
                    del posts[i]
                    break
            f = open('./static/json/test.json', 'w')
            json.dump(posts, f, indent="\t")
            f.close()
            return redirect(url_for('test_post'))
        if request.form['check'] == 'edit':
            pid = int(request.form['id'])
            for i in range(len(posts)):
                if posts[i]['id'] == pid:
                    f.close()
                    return render_template("edit.html", epost=posts[i])
    return render_template("test_post.html", year=year, all_posts=posts)


@app.route("/algo_post", methods=["GET", "POST"])
def algo_post():
    f = open('./static/json/algo.json', 'r')
    posts = json.load(f)
    f.close()
    if request.method == "POST":
        if request.form['check'] == 'del':
            pid = int(request.form['id'])
            for i in range(len(posts)):
                if posts[i]['id'] == pid:
                    del posts[i]
                    break
            f = open('./static/json/algo.json', 'w')
            json.dump(posts, f, indent="\t")
            f.close()
            return redirect(url_for('algo_post'))
        if request.form['check'] == 'edit':
            pid = int(request.form['id'])
            for i in range(len(posts)):
                if posts[i]['id'] == pid:
                    f.close()
                    return render_template("edit.html", epost=posts[i])
    return render_template("algo_post.html", year=year, all_posts=posts)


#로그인 확인
@app.before_request
def load_logged_in_user():
    manager_id = session.get('manager')
    if manager_id is None:
        g.user = None
    else:
        g.user = manager_id


#로그아웃
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


#포스팅 추가
@app.route('/add', methods=["GET", "POST"])
def add_post():
    if request.method == "POST":
        data = request.form
        d = datetime.now()
        new = {
            "id": 0,
            "category": data['category'],
            "title": data['Title'],
            "subtitle": data['Sub'],
            "author": g.user,
            "date": str(d.year) + '년' + str(d.month) + '월' + str(d.day) + '일',
            "body": data.get('ckeditor')
        }
        if data['category'] == 'Blog':
            add_blogjson(new)   #아래에 함수 있음
            return redirect(url_for('blog_post'))
        elif data['category'] == "Test":
            add_testjson(new)
            return redirect(url_for('test_post'))
        elif data['category'] == 'Algo':
            add_algojson(new)
            return redirect(url_for('algo_post'))
    return render_template("add_post.html")


#포스트 편집
@app.route('/edit', methods=["GET", "POST"])
def edit_post():
    if request.method == "POST":
        data = request.form
        if data['category'] == 'Blog':
            with open('./static/json/post.json', 'r') as file:
                posts = json.load(file)
                for i in range(len(posts)):
                    if posts[i]['id'] == int(data['id']):
                        posts[i]['title'] = data['Title']
                        posts[i]['subtitle'] = data['Sub']
                        posts[i]['body'] = data.get('ckeditor')
                        break
            with open('./static/json/post.json', 'w') as file:
                json.dump(posts, file, indent=4)
            return redirect(url_for('blog_post'))
        elif data['category'] == 'Test':
            with open('./static/json/Test.json', 'r') as file:
                posts = json.load(file)
                for i in range(len(posts)):
                    if posts[i]['id'] == int(data['id']):
                        posts[i]['title'] = data['Title']
                        posts[i]['subtitle'] = data['Sub']
                        posts[i]['body'] = data.get('ckeditor')
                        break
            with open('./static/json/Test.json', 'w') as file:
                json.dump(posts, file, indent=4)
            return redirect(url_for('test_post'))
        elif data['category'] == 'Algo':
            with open('./static/json/algo.json', 'r') as file:
                posts = json.load(file)
                for i in range(len(posts)):
                    if posts[i]['id'] == int(data['id']):
                        posts[i]['title'] = data['Title']
                        posts[i]['subtitle'] = data['Sub']
                        posts[i]['body'] = data.get('ckeditor')
                        break
            with open('./static/json/algo.json', 'w') as file:
                json.dump(posts, file, indent=4)
            return redirect(url_for('algo_post'))


#메일 보내는 함수
def send_email(name, email, phone, message):
    email_message = f"Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(OWN_EMAIL, OWN_PASSWORD)
        connection.sendmail(OWN_EMAIL, OWN_EMAIL, email_message)


#블로그 포스트 추가 함수
def add_blogjson(new_post, filename='./static/json/post.json'):
    with open(filename, 'r+') as file:
        file_content = json.load(file)
        if len(file_content) == 0:
            new_post['id'] = 0
        else:
            new_post['id'] = file_content[len(file_content)-1]['id'] + 1
        file_content.append(new_post)
        file.seek(0)
        json.dump(file_content, file, indent=4)


#테스트 포스트 추가 함수
def add_testjson(new_post, filename='./static/json/Test.json'):
    with open(filename, 'r+') as file:
        file_content = json.load(file)
        if len(file_content) == 0:
            new_post['id'] = 0
        else:
            new_post['id'] = file_content[len(file_content)-1]['id'] + 1
        file_content.append(new_post)
        file.seek(0)
        json.dump(file_content, file, indent=4)


def add_algojson(new_post, filename='./static/json/algo.json'):
    with open(filename, 'r+') as file:
        file_content = json.load(file)
        if len(file_content) == 0:
            new_post['id'] = 0
        else:
            new_post['id'] = file_content[len(file_content)-1]['id'] + 1
        file_content.append(new_post)
        file.seek(0)
        json.dump(file_content, file, indent=4)


if __name__ == "__main__":
    year = str(date.today().year)
    app.run(debug=True)