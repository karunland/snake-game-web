import json
import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.run('0.0.0.0', 5000)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///game.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=['POST', 'GET'])
@login_required
def index():
    user_id = session['user_id']
    return render_template('main.html')


@app.route('/get/score', methods=['POST'])
@login_required
def get_score():
    print('get_score triggered')
    user_id = session['user_id']
    data = json.loads(request.data)
    db.execute('INSERT INTO scores (id, score) VALUES (?, ?)',
               user_id, data['score'])
    return '{"return": "ok"}', 200


@app.route("/scores")
@login_required
def scores():
    user_id = session['user_id']
    data = db.execute('select users.username, scores.score\
                        FROM users\
                        INNER JOIN scores ON users.id=scores.id\
                        ORDER By scores.score DESC;')
    scores_by_user = {}

    for score in data:
        username = score['username']
        if username not in scores_by_user:
            scores_by_user[username] = []
        scores_by_user[username].append(score['score'])

    filtered_scores = {}

    for username, scores in scores_by_user.items():
        filtered_scores[username] = [score for score in scores if score > 0]

    high_scores = {}

    for username, scores in scores_by_user.items():
        high_score = max(scores)
        high_scores[username] = high_score

    print(high_scores)
    for index, key in high_scores.items():
        print(f'{index} {key}')
    return render_template('scores.html', high_scores=dict(high_scores))


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username")

        elif not request.form.get("password"):
            return apology("must provide password")

        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        session["user_id"] = rows[0]["id"]

        return redirect("/")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == 'POST':
        if not request.form.get('username'):
            return apology('username is req')
        elif not request.form.get('password'):
            return apology('password is req')
        elif not request.form.get('confirmation'):
            return apology('confirmation is req')

        if request.form.get('password') != request.form.get('confirmation'):
            return apology('pass didnt match with confirmation pass')

        hashed_password = generate_password_hash(
            password=request.form.get('password'))
        try:
            db.execute('INSERT INTO users (username, hash) VALUES (?, ?)',
                       request.form.get('username'), hashed_password)
            return redirect('/')
        except:
            return apology('username\'s exist')

    return render_template('register.html')
