from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), nullable = False, unique = True) 
    password = db.Column(db.String(200), nullable = False)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable = False, unique = True)
    password = db.Column(db.String(200), nullable = False)
    website = db.Column(db.String(200), nullable = True)
    industry = db.Column(db.String(100), nullable = True)
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default = False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable = False, unique = True)
    password = db.Column(db.String(200), nullable = False)
    department = db.Column(db.String(100), nullable = False)
    is_active = db.Column(db.Boolean, default=True)
    resume = db.Column(db.String(200), nullable = True)
    skills = db.Column(db.String(200), nullable = True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    description = db.Column(db.Text, nullable = False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    status = db.Column(db.String(20), default = "pending")
    skills = db.Column(db.String(200), nullable = True)
    experience = db.Column(db.String(100), nullable = True)
    salary = db.Column(db.String(200), nullable = True)
    deadline = db.Column(db.String(200), nullable = True)
    company = db.relationship('Company', backref='jobs')
    eligibility = db.Column(db.String(200), nullable = True)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    status = db.Column(db.String(50), default = "applied")
    notified = db.Column(db.Boolean, default = False)
    student = db.relationship('Student', backref='applications')
    job = db.relationship('Job', backref='applications')

class Placement(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'))
    salary = db.Column(db.String(100), nullable = True)
    joining_date = db.Column(db.String(100), nullable = True)
    application = db.relationship('Application', backref='placement')