from flask import Flask, render_template, request
from datetime import date
import requests
import smtplib

app = Flask(__name__)
posts = requests.get("https://api.npoint.io/00702af2453468366801").json()
OWN_EMAIL = "5658love5658@gmail.com"
OWN_PASSWORD = "svikaanwyilxmwdh"

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


def send_email(name, email, phone, message):
    email_message = f"Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(OWN_EMAIL, OWN_PASSWORD)
        connection.sendmail(OWN_EMAIL, OWN_EMAIL, email_message)

if __name__ == "__main__":
    year = str(date.today().year)
    app.run(debug=True)