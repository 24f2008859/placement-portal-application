from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy 
from models import db, Admin, Company, Student, Job, Application, Placement
import os

app = Flask(__name__)
app.secret_key = "placeme_secret"
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static/resumes')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placeme.db"
db.init_app(app)
app.app_context().push()

@app.route("/", methods = ["GET", "POST"])
def home():
    latest_drives = Job.query.filter_by(status = 'approved').limit(3).all()
    return render_template("home.html", latest_drives=latest_drives)


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Validation
        if not email or not password:
            flash("Email and password are required!", "danger")
            return render_template("login.html")
        
        if len(password) < 6:
            flash("password must be at least 6 characters!", "danger")
            return render_template("login.html")
        
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

@app.route("/student_register", methods=["GET","POST"])
def student_register():
    if request.method == "POST":
        # 1. get all form data
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        department = request.form.get("department")
        skills = request.form.get("skills")
        # 2. Validate
        errors = []
        if not name or len(name) < 3:
            errors.append("Name must be atleast 3 characters")
        if not email or "@" not in email:
            errors.append("Invalid email address")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters!")
        confirm_password = request.form.get("confirm-password")
        if password != confirm_password:
            errors.append("Passwords do not match")
        if not department:
            errors.append("Department is required!")
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("student_register.html")
        
        existing = Student.query.filter_by(email=email).first()
        if existing:
            flash("Email already registered!", "danger")
        else:
            new_student = Student(name=name, email=email, password=password, department=department, skills=skills)
            file = request.files.get("resume")
            if file and file.filename != "":
                filename = f"student_{email}_{file.filename.replace(' ', '_')}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_student.resume = filename
            db.session.add(new_student)
            db.session.commit()
            flash("Registration successful!", "success")
            return redirect(url_for('home'))
    return render_template("student_register.html")


@app.route("/recruiter_register", methods=["GET","POST"])
def recruiter_register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        industry = request.form.get("industry")
        website = request.form.get("website")

        errors = []
        if not name or len(name) < 3:
            errors.append("Name must be atleast 3 characters")
        if not email or "@" not in email:
            errors.append("Invalid email address")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters!")
        confirm_password = request.form.get("confirm-password")
        if password != confirm_password:
            errors.append("Passwords do not match")
        if not industry:
            errors.append("Industry is required!")
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("recruiter_register.html")

        existing = Company.query.filter_by(email=email).first()
        if existing:
            flash("Email already registered!", "danger")
        else:
            new_recruiter = Company(name=name, email=email, password=password, industry=industry, website=website)
            db.session.add(new_recruiter)
            db.session.commit()
            flash("Registration submitted! Wait for Admin approval.", "success")
            return redirect(url_for('home'))
    return render_template("recruiter_register.html")



@app.route("/admin_dashboard")
def admin_dashboard():
    if session.get('role') != 'admin':
        flash("Please login first!", "warning")
        return redirect(url_for('home'))
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = Job.query.count()
    total_applications = Application.query.count()
    pending_companies = Company.query.filter_by(is_approved=False, is_active=True).all()
    pending_drives = Job.query.filter_by(status = 'pending').all()
    all_drives = Job.query.all()
    all_applications = Application.query.all()
    
    search_student = request.args.get("search_student", "")
    search_company = request.args.get("search_company", "")

    if search_student:
        all_students = Student.query.filter(
            Student.name.contains(search_student) |
            Student.email.contains(search_student) |
            Student.id == (int(search_student) if search_student.isdigit() else -1)
        ).all()
    else:
        all_students = Student.query.all()

    if search_company:
        all_companies = Company.query.filter(
            Company.name.contains(search_company) |
            Company.industry.contains(search_company) |
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
            pending_drives = pending_drives,
            all_students = all_students,
            all_companies = all_companies,
            all_drives = all_drives,
            all_applications = all_applications)

@app.route("/student_dashboard")
def student_dashboard():
    if session.get('role') != 'student':
        flash("Please login first!", "warning")
        return redirect(url_for('home'))
    student = Student.query.get(session['student_id'])
    my_applications = Application.query.filter_by(student_id = student.id).all()
    applied_job_ids = [app.job_id for app in my_applications]
    search = request.args.get("search", "")
    if search:
        approved_drives = Job.query.filter(Job.status == 'approved', Job.title.contains(search) | Job.skills.contains(search) | Job.company.has(Company.name.contains(search))).all()
    else:
        approved_drives = Job.query.filter_by(status = 'approved').all()
    notifications = Application.query.filter_by(student_id=student.id, notified=False).filter(Application.status != 'applied').all()
    return render_template("student_dashboard.html", student=student, approved_drives = approved_drives, my_applications = my_applications, applied_job_ids = applied_job_ids, search=search, notifications=notifications)

@app.route("/company_dashboard" )
def company_dashboard():
    if session.get('role') != 'company':
        flash("Please login first!", "warning")
        return redirect(url_for('home'))
    company = Company.query.get(session['company_id'])
    drives = Job.query.filter_by(company_id = company.id).all()
    return render_template("company_dashboard.html", company = company, drives=drives)

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

@app.route("/create_drive", methods=["POST"])
def create_drive():
    if session.get('role') != 'company':
        return redirect(url_for('home'))
    company_id = session['company_id']
    company = Company.query.get(company_id)
    if not company.is_active:
        flash("You are blacklisted and can't create drives.", "danger")
        return redirect(url_for('company_dashboard'))
    title = request.form.get("title")
    description = request.form.get("description")
    skills = request.form.get("skills")
    experience = request.form.get("experience")
    salary = request.form.get("salary")
    deadline = request.form.get("deadline")
    eligibility = request.form.get("eligibility")
    

    errors = []
    if not title:
        errors.append("Job title is required!")
    if not description:
        errors.append("Job description is required!")
    if not deadline:
        errors.append("Application deadline is required!")
    if errors:
        for error in errors:
            flash(error, "danger")
        return redirect(url_for('company_dashboard'))

    new_drive = Job(title = title, description=description, company_id=company_id, skills = skills, experience = experience, salary = salary, deadline = deadline, eligibility=eligibility)
    db.session.add(new_drive)
    db.session.commit()
    flash("Drive created! Waiting for admin approval.", "success")
    return redirect(url_for('company_dashboard'))


@app.route("/view_applications/<int:drive_id>")
def view_applications(drive_id):
    if session.get('role') != 'company':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('home'))
    drive = Job.query.get(drive_id)
    applications = Application.query.filter_by(job_id = drive_id).all()
    return render_template("view_applications.html", drive=drive, applications=applications)


@app.route("/update_application/<int:application_id>", methods= ["POST"])
def update_application(application_id):
    if session.get('role') != 'company':
        return redirect(url_for('home'))
    status = request.form.get("status")
    application = Application.query.get(application_id)
    application.status = status
    application.notified = False
    db.session.commit()
    flash("Application status updated!", "success")
    return redirect(url_for('view_applications', drive_id = application.job_id))

@app.route("/apply/<int:drive_id>", methods = ["POST"])
def apply(drive_id):
    if session.get('role') != 'student':
        return redirect(url_for('home'))
    student_id = session['student_id']
    student = Student.query.get(student_id)
    if not student.is_active:
        flash("You are blacklisted and can't apply for jobs.", "danger")
        return redirect(url_for('student_dashboard'))
    existing = Application.query.filter_by(student_id = student_id, job_id = drive_id).first()
    if existing:
        flash("already applied!", "warning")
    else:
        new_application = Application(student_id = student_id, job_id = drive_id)
        db.session.add(new_application)
        db.session.commit()
        flash("applied successfully!", "success")
    return redirect(url_for('student_dashboard'))

@app.route("/approve_drive/<int:drive_id>", methods = ["POST"])
def approve_drive(drive_id):
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    drive = Job.query.get(drive_id)
    drive.status = 'approved'
    db.session.commit()
    flash("Drive approved!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route("/reject_drive/<int:drive_id>", methods = ["POST"])
def reject_drive(drive_id):
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    drive = Job.query.get(drive_id)
    drive.status = 'rejected'
    db.session.commit()
    flash("Drive rejected!", "danger")
    return redirect(url_for('admin_dashboard'))

@app.route("/toggle_drive_status/<int:drive_id>", methods = ["POST"])
def toggle_drive_status(drive_id):
    if session.get('role') != 'company':
        return redirect(url_for('home'))
    drive = Job.query.get(drive_id)
    if drive.status == 'approved':
        drive.status = 'closed'
    else:
        drive.status = 'approved'
    db.session.commit()
    flash("Drive status updated!", "success")
    return redirect(url_for('company_dashboard'))


@app.route("/update_profile", methods=["GET","POST"])
def update_profile():
    if session.get('role') != 'student':
        return redirect(url_for('home'))
    student = Student.query.get(session['student_id'])
    if request.method == "POST":
        student.name = request.form.get("name")
        student.department = request.form.get("department")
        student.skills = request.form.get("skills")
        file = request.files.get("resume")
        if file and file.filename != "":
            filename = f"student_{student.id}_{file.filename.replace(' ','_')}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            student.resume = filename
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('student_dashboard'))
    return render_template("update_profile.html", student = student)

@app.route("/mark_notified/<int:application_id>", methods=["POST"])
def mark_notified(application_id):
    application = Application.query.get(application_id)
    application.notified = True 
    db.session.commit()
    return redirect(url_for('student_dashboard'))

@app.route("/api/students", methods = ["GET"])
def api_students():
    students = Student.query.all()
    return jsonify([{
        "id": s.id,
        "name": s.name,
        "email": s.email,
        "department": s.department,
        "skills": s.skills
    } for s in students])

@app.route("/api/companies", methods = ["GET"])
def api_companies():
    companies = Company.query.all()
    return jsonify([{
        "id": c.id,
        "name": c.name,
        "email": c.email,
        "industry": c.industry,
        "website": c.website,
        "is_approved": c.is_approved
    } for c in companies])

@app.route("/api/jobs", methods = ["GET"])
def api_jobs():
    jobs = Job.query.all()
    return jsonify([{
        "id": j.id,
        "title": j.title,
        "description": j.description,
        "experience": j.experience,
        "salary": j.salary,
        "skills": j.skills,
        "deadline": j.deadline,
        "status": j.status,
        "company": j.company.name
    } for j in jobs])

@app.route("/api/applications", methods = ["GET"])
def api_applications():
    applications = Application.query.all()
    return jsonify([{
        "id": a.id,
        "student": a.student.name,
        "job": a.job.title,
        "company": a.job.company.name,
        "status": a.status
    } for a in applications])

@app.route("/api/jobs", methods = ["POST"])
def api_create_job():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    title = data.get("title")
    description = data.get("description")
    company_id = data.get("company_id")
    if not title or not description or not company_id:
        return jsonify({"error": "Title, description and company_id are required"})
    new_job = Job(title=title, description=description, company_id=company_id)
    db.session.add(new_job)
    db.session.commit()
    return jsonify({"message": "Job created!", "id": new_job.id}), 201

@app.route("/api/applications/<int:application_id>", methods=["PUT"])
def api_update_application(application_id):
    application = Application.query.get(application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404
    data = request.get_json()
    status = data.get("status")
    if not status:
        return jsonify({"error": "Status is required"}), 400
    application.status = status
    db.session.commit()
    return jsonify({"message": "Status updated!", "status": application.status})

@app.route("/api/jobs/<int:job_id>", methods=["DELETE"])
def api_delete_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Job deleted!"}), 200

with app.app_context():
    db.create_all()
    if not Admin.query.first():
        admin = Admin(username="admin", password="admin123")
        db.session.add(admin)
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)