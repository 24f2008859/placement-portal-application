from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy 
from models import db, User, Job, Application 

app = Flask(__name__)
app.secret_key = "placeme_secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placeme.db"
db.init_app(app)
app.app_context().push()

@app.route("/", methods = ["GET", "POST"])
def home():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
           return redirect(url_for('home'))
        else:
            flash("Invalid credentials")
    return render_template("login.html")



@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")
        role = request.form.get("role")
        department = request.form.get("department")
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered", "danger" )
        else:
            new_user = User(name = name, email = email, password = password, role = role, department = department)
            db.session.add(new_user)
            db.session.commit()
            flash("successful", "success")
            return redirect(url_for('home'))
    return render_template("register.html")



with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)