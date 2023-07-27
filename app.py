import secrets
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import bcrypt
from functools import wraps

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///leaderboard.db"
app.config["SQLALCHEMY_BINDS"] = {"login": "sqlite:///users.db"}
db = SQLAlchemy(app)
migrate = Migrate(app, db)


def generate_secret_key():
    return secrets.token_hex(64)


app.secret_key = generate_secret_key()


class Ranking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)


def initdb():
    with app.app_context():
        db.create_all()


def is_logged_in():
    return "username" in session


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/game")
def game():
    return render_template(
        "game.html", is_logged_in=is_logged_in(), username=session.get("username")
    )


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/rankings", methods=["POST"])
def saveRanking():
    user = request.json.get("user")
    score = request.json.get("score")
    ranking = Ranking(user=user, score=score, end_time=datetime.utcnow())
    with app.app_context():
        db.session.add(ranking)
        db.session.commit()
    return jsonify({"message": "Ranking submitted successfully"})


@app.route("/rankings")
def leaderboard():
    with app.app_context():
        rankings = Ranking.query.order_by(Ranking.score.desc()).all()
        ranked_data = [
            (
                rank,
                entry.user,
                entry.score,
                entry.end_time.strftime("%Y-%m-%d "),
            )
            for rank, entry in enumerate(rankings, start=1)
        ]
    return render_template(
        "rankings.html", ranked_data=ranked_data, is_logged_in=is_logged_in()
    )


@app.route("/login", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect(url_for("game"))

    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password_candidate = request.form.get("password")

        if not username or not password_candidate:
            error = "Please provide both username and password."
        else:
            username = username.strip()
            password_candidate = password_candidate.strip()

            user = User.query.filter_by(username=username).first()

            if user and bcrypt.verify(password_candidate, user.password):
                session["username"] = username
                return redirect(url_for("game"))
            else:
                error = "Invalid credentials. Please try again."

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    if is_logged_in():
        return redirect(url_for("game"))

    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            error = "Please provide both username and password."
        else:
            username = username.strip()
            password = password.strip()

            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                error = "Username already exists. Please choose a different username."
            else:
                if (
                    len(password) < 8
                    or not any(char.isdigit() for char in password)
                    or not any(char.isalnum() for char in password)
                ):
                    error = "Password must be at least 8 characters long and contain numbers and special characters."
                else:
                    hashed_password = bcrypt.hash(password)
                    user = User(username=username, password=hashed_password)
                    with app.app_context():
                        db.session.add(user)
                        db.session.commit()
                        return redirect(url_for("login"))

    return render_template("register.html", error=error)


if __name__ == "__main__":
    initdb()
    app.run(debug=True)
