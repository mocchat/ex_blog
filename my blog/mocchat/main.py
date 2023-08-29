from flask import Flask, render_template, request, session, flash, g\
    , Blueprint, redirect, url_for
from datetime import date, datetime
import requests
import smtplib
import hashlib
import pymysql
import json

app = Flask(__name__)
OWN_EMAIL = "5658love5658@gmail.com"
OWN_PASSWORD = "svikaanwyilxmwdh"
app.config["SECRET_KEY"] = "ABCD"
bp = Blueprint("auth", __name__, url_prefix="/user")

conn = pymysql.connect(host='localhost', user='root', password='!aa47287846', db='blog_db', charset='utf8')
cur = conn.cursor()

cur.execute('select passward from manager')
pwd = cur.fetchall()[0][0]



@app.route('/')
@app.route('/index.html', methods=["GET", "POST"])
def home():
    f = open('./static/json/post.json', 'r')
    posts = json.load(f)
    if request.method == "POST":
        pid = int(request.form['id'])
        for i in range(len(posts)):
            if posts[i]['id'] == pid:
                del posts[i]
                break
        f = open('./static/json/post.json', 'w')
        json.dump(posts, f, indent="\t")
        f.close()
        return redirect(url_for('home'))
    f.close()
    return render_template("index.html", year=year, all_posts=posts)


@app.route('/<string:page>')
def page(page: str):
    return render_template(page, year=year)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    f = open('./static/json/post.json', 'r')
    posts = json.load(f)
    f.close()
    for blog_post in posts:
        if blog_post["id"] == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        data = request.form
        send_email(data["name"], data["email"], data["phone"], data["message"])
        return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", msg_sent=False)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        error = None
        password = request.form['password']
        m = hashlib.sha256()
        m.update(password.encode('utf-8'))  #f6f2ea8f45d8a057c9566a33f99474da2e5c6a6604d736121650e2730c6fb0a3
        if m.hexdigest() != pwd:
            error = "비밀번호가 올바르지 않습니다."
        if error is None:
            session.clear()
            session['manager'] = 'login'
            return redirect(url_for('home'))
        flash(error)
    return render_template("login.html")


@app.before_request
def load_logged_in_user():
    manager_id = session.get('manager')
    if manager_id is None:
        g.user = None
    else:
        g.user = manager_id


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/add', methods=["GET", "POST"])
def add_post():
    if request.method == "POST":
        data = request.form
        d = datetime.now()
        new = {
            "id": 0,
            "title": data['Title'],
            "subtitle": data['Sub'],
            "author": 'manager',
            "date": str(d.year) + '년' + str(d.month) + '월' + str(d.day) + '일',
            "body": data['Body']
        }
        add_json(new)
        return redirect(url_for('home'))
    return render_template("add_post.html")


def send_email(name, email, phone, message):
    email_message = f"Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(OWN_EMAIL, OWN_PASSWORD)
        connection.sendmail(OWN_EMAIL, OWN_EMAIL, email_message)


def add_json(new_post, filename='./static/json/post.json'):
    with open(filename, 'r+') as file:
        file_content = json.load(file)
        if len(file_content) == 0:
            new_post['id'] = 0
        else:
            new_post['id'] = file_content[len(file_content)-1]['id'] + 1
        file_content.append(new_post)
        file.seek(0)
        json.dump(file_content, file, indent=4)
        file.close()


if __name__ == "__main__":
    year = str(date.today().year)
    app.run(debug=True)