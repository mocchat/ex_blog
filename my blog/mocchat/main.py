from flask import Flask, render_template, request, session, flash, g\
    , Blueprint, redirect, url_for
from datetime import date
import requests
import smtplib
import hashlib
import pymysql

app = Flask(__name__)
posts = requests.get("https://api.npoint.io/00702af2453468366801").json()
OWN_EMAIL = "5658love5658@gmail.com"
OWN_PASSWORD = "svikaanwyilxmwdh"
app.config["SECRET_KEY"] = "ABCD"
bp = Blueprint("auth", __name__, url_prefix="/user")
conn = pymysql.connect(host='localhost', user='root', password='!aa47287846', db='blog_db', charset='utf8')
cur = conn.cursor()

cur.execute('select password from manager where manager_id = 2')
pwd = cur.fetchall()[0][0]


@app.route('/')
@app.route('/index.html')
def home():
    return render_template("index.html", year=year, all_posts=posts)


@app.route('/<string:page>')
def page(page: str):
    return render_template(page, year=year)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
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
        m.update(password.encode('utf-8'))
        print(pwd, m.hexdigest(), 'gg')
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


def send_email(name, email, phone, message):
    email_message = f"Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(OWN_EMAIL, OWN_PASSWORD)
        connection.sendmail(OWN_EMAIL, OWN_EMAIL, email_message)


if __name__ == "__main__":
    year = str(date.today().year)
    app.run(debug=True)