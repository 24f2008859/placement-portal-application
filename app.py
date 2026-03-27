from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy 
from models import db, Admin, Company, Student, Job, Application, Placement

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
        admin = Admin.query.filter_by(username=email).first()
        student = Student.query.filter_by(email=email).first()
        company = Company.query.filter_by(email=email).first()
        if admin and admin.password == password:
            return redirect(url_for('admin_dashboard'))
        elif student and student.password == password:
           return redirect(url_for('student_dashboard'))
        elif company and company.password == password:
            if company.is_approved:
                return redirect(url_for('company_dashboard'))
            else:
                flash("Waiting for admin approval", "warning")
        else:
            flash("Invalid credentials")
    return render_template("login.html")




@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        role = request.form.get("role")
        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")
        department = request.form.get("department")
        existing_user1 = Student.query.filter_by(email=email).first()
        existing_user2 = Company.query.filter_by(email=email).first()
        if existing_user1 or existing_user2:
            flash("Email already registered", "danger" )
        else:
            if role == 'student':
                new_user = Student(name = name, email = email, password = password, department = department)
                db.session.add(new_user)
                db.session.commit()
                flash("Registration successful", "success")
                return redirect(url_for('home'))
            elif role == 'recruiter':
                website = request.form.get("website")
                new_user = Company(name = name, email = email, password = password, website= website)
                db.session.add(new_user)
                db.session.commit()
                flash("Registration submitted! wait for Admin approval.", "success")
                return redirect(url_for('home'))
    return render_template("register.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route("/student_dashboard")
def student_dashboard():
    return render_template("student_dashboard.html")

@app.route("/company_dashboard" )
def company_dashboard():
    return render_template("company_dashboard.html")


with app.app_context():
    db.create_all()
if not Admin.query.first():
    admin = Admin(username="admin", password="admin123")
    db.session.add(admin)
    db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)