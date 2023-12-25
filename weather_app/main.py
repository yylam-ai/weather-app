from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from weather.weather import weather

app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(days=5)
app.register_blueprint(weather, url_prefix="/weather")

db = SQLAlchemy(app)

class users(db.Model):
     _id = db.Column("id", db.Integer, primary_key=True)
     name = db.Column(db.String(100), unique=True)
     password = db.Column(db.String(100))

     def __init__(self, name, password):
         self.name = name
         self.password = password

@app.route("/signup", methods=["POST", "GET"])
def register():
    if request.method == "POST" and request.form["register_username"] == "":
        flash("Please enter username!", "error")

    elif request.method == "POST":
        user = request.form["register_username"]
        pwd = request.form["register_password"]
        cfm_pwd = request.form["cfm_password"]

        if pwd == cfm_pwd:
            usr = users(user, pwd)
            try:
                db.session.add(usr)
                db.session.commit()
                flash("Account Registered", 'success')
                return redirect(url_for("login"))
            except:
                flash("Account already exists" ,"error")        
        else:
            flash("Password does not match", "error")

    return render_template("signup.html")


@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST" and (request.form["name"] == "" or request.form["password"]==""):
        flash("Please enter Username or Password!", "error")

    elif request.method == "POST":
        session.permanent = True
        user = request.form["name"]
        session["user"] = user

        found_user = users.query.filter_by(name=user).first()
        if found_user and request.form['password'] == found_user.password:
                session["usr_id"] = found_user._id
                flash("Login Succesful!") 
        else:
            flash("Invalid combination", "error")
            return render_template("login.html")
        
        return redirect(url_for("weather.index_get"))
    else:
        if "user" in session:
            flash("Already logged in!")
            return redirect(url_for("weather.index_get"))

    return render_template("login.html")


@app.route('/logout')
def logout():
    flash("You have been logged out")
    session.pop("user", None)
    session.pop("usr_id", None)
    return redirect(url_for("login"))

if "__main__":
    db.create_all()
    app.run(debug=True)