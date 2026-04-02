from app import app, db
from models import Student, Company

with app.app_context():
    # Students
    s1 = Student(name="Test Student 1", email="student1@test.com",
                password="test123", department="CS")
    s2 = Student(name="Test Student 2", email="student2@test.com",
                password="test123", department="Electronics")
    s3 = Student(name="Test Student 3", email="student3@test.com",
                password="test123", department="Mechanical")

    # Companies
    c1 = Company(name="Google", email="google@test.com",
                password="test123", website="google.com",
                industry="Software")
    c2 = Company(name="Amazon", email="amazon@test.com",
                password="test123", website="amazon.com",
                industry="E-Commerce")
    c3 = Company(name="Infosys", email="infosys@test.com",
                password="test123", website="infosys.com",
                industry="IT Services")

    # Add all at once
    db.session.add_all([s1, s2, s3, c1, c2, c3])
    db.session.commit()
    print("Seed data added!")