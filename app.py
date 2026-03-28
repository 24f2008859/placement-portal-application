from flask import Flask, render_template, request, redirect, url_for, flash, session
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
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        elif student and student.password == password:
           session['role'] = 'student'
           session['student_id'] = student.id
           return redirect(url_for('student_dashboard'))
        elif company and company.password == password:
            if company.is_approved:
                session['role'] = 'company'
                session['company_id'] = company.id
                return redirect(url_for('company_dashboard'))
            else:
                flash("Waiting for admin approval", "warning")
        else:
            flash("Invalid credentials")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for('home'))

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
                new_user = Company(name = name, email = email, password = password, website= website, industry= department)
                db.session.add(new_user)
                db.session.commit()
                flash("Registration submitted! wait for Admin approval.", "success")
                return redirect(url_for('home'))
    return render_template("register.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    if session.get('role') != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('home'))
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = Job.query.count()
    total_applications = Application.query.count()
    pending_companies = Company.query.filter_by(is_approved=False, is_active=True).all()
    
    search_student = request.args.get("search_student", "")
    search_company = request.args.get("search_company", "")

    if search_student:
        all_students = Student.query.filter(
            Student.name.contains(search_student) |
            Student.id == (int(search_student) if search_student.isdigit() else -1)
        ).all()
    else:
        all_students = Student.query.all()

    if search_company:
        all_companies = Company.query.filter(
            Company.name.contains(search_company) |
            Company.id == (int(search_company) if search_company.isdigit() else -1)
        ).all()
    else:
        all_companies = Company.query.all()
    return render_template("admin_dashboard.html",
            total_students = total_students,
            total_companies = total_companies,
            total_drives = total_drives,
            total_applications = total_applications,
            pending_companies = pending_companies,
            all_students = all_students,
            all_companies = all_companies)

@app.route("/student_dashboard")
def student_dashboard():
    if session.get('role') != 'student':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('home'))
    return render_template("student_dashboard.html")

@app.route("/company_dashboard" )
def company_dashboard():
    if session.get('role') != 'company':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('home'))
    return render_template("company_dashboard.html")

@app.route("/approve_company/<int:company_id>", methods=["POST"])
def approve_company(company_id):
    company = Company.query.get(company_id)
    company.is_approved = True
    db.session.commit()
    flash("Company approved!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route("/reject_company/<int:company_id>", methods=["POST"])
def reject_company(company_id):
    company = Company.query.get(company_id)
    company.is_active = False
    db.session.commit()
    flash("Company rejected!", "danger")
    return redirect(url_for('admin_dashboard'))

@app.route("/blacklist_student/<int:student_id>", methods=["POST"])
def blacklist_student(student_id):
    student = Student.query.get(student_id)
    student.is_active = not student.is_active
    db.session.commit()
    flash("Student status updated!", "success")
    return redirect(url_for('admin_dashboard'))


@app.route("/blacklist_company/<int:company_id>", methods=["POST"])
def blacklist_company(company_id):
    company = Company.query.get(company_id)
    company.is_active = not company.is_active
    db.session.commit()
    flash("Company status updated!", "success")
    return redirect(url_for('admin_dashboard'))

with app.app_context():
    db.create_all()
    if not Admin.query.first():
        admin = Admin(username="admin", password="admin123")
        db.session.add(admin)
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)