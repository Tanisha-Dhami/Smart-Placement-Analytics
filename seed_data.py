from mysql_db import execute, query_all
from mongodb_db import save_skills, add_feedback, ensure_indexes

def seed():
    # Example data is inserted only when the relevant record is not already present.
    students = [
        ("Aarav Sharma", "aarav@example.com", "CSE", 6),
        ("Meera Kaur", "meera@example.com", "AI & ML", 6),
        ("Kabir Singh", "kabir@example.com", "IT", 6),
    ]
    for name, email, dept, sem in students:
        if not query_all("SELECT student_id FROM students WHERE email=%s", (email,)):
            execute("INSERT INTO students(name,email,department,semester) VALUES(%s,%s,%s,%s)", (name,email,dept,sem))

    courses = [("Database Management Systems", 4), ("Python Programming", 3), ("Machine Learning", 4)]
    for course, credits in courses:
        if not query_all("SELECT course_id FROM courses WHERE course_name=%s", (course,)):
            execute("INSERT INTO courses(course_name,credits) VALUES(%s,%s)", (course,credits))

    companies = [("DataNova", "Technology"), ("CloudPeak", "Cloud Services")]
    for company, industry in companies:
        if not query_all("SELECT company_id FROM companies WHERE company_name=%s", (company,)):
            execute("INSERT INTO companies(company_name,industry) VALUES(%s,%s)", (company,industry))

    student_ids = {r["email"]: r["student_id"] for r in query_all("SELECT student_id,email FROM students")}
    course_ids = {r["course_name"]: r["course_id"] for r in query_all("SELECT course_id,course_name FROM courses")}
    sample_marks = [
        ("aarav@example.com", "Database Management Systems", 86),
        ("aarav@example.com", "Python Programming", 82),
        ("meera@example.com", "Database Management Systems", 91),
        ("meera@example.com", "Machine Learning", 89),
        ("kabir@example.com", "Python Programming", 76),
    ]
    for email, course, marks in sample_marks:
        sid, cid = student_ids[email], course_ids[course]
        if not query_all("SELECT mark_id FROM marks WHERE student_id=%s AND course_id=%s AND semester=%s", (sid,cid,6)):
            execute("INSERT INTO marks(student_id,course_id,marks,semester) VALUES(%s,%s,%s,%s)", (sid,cid,marks,6))

    company_ids = {r["company_name"]: r["company_id"] for r in query_all("SELECT company_id,company_name FROM companies")}
    placement_samples = [
        ("meera@example.com", "DataNova", "Junior Data Analyst", 5.5, "Selected"),
        ("aarav@example.com", "CloudPeak", "Intern", 3.0, "Interview"),
    ]
    for email, company, role, package, status in placement_samples:
        sid, cid = student_ids[email], company_ids[company]
        if not query_all("SELECT placement_id FROM placements WHERE student_id=%s AND company_id=%s AND job_role=%s", (sid,cid,role)):
            execute("INSERT INTO placements(student_id,company_id,job_role,package_lpa,status,placement_date) VALUES(%s,%s,%s,%s,%s,CURDATE())", (sid,cid,role,package,status))

    ensure_indexes()
    for email, skills, certs, projects in [
        ("aarav@example.com", "Python, SQL, Excel", "SQL Basics", "Placement Analytics Mini Project"),
        ("meera@example.com", "Python, SQL, Machine Learning", "AI Fundamentals, Python Certificate", "Student Placement Analytics"),
        ("kabir@example.com", "Python, MongoDB", "Python Certificate", "Student Record Manager"),
    ]:
        save_skills(student_ids[email], skills, certs, projects)
    if not query_all("SELECT student_id FROM students WHERE email=%s", ("meera@example.com",)):
        return
    meera_id = student_ids["meera@example.com"]
    existing = query_all("SELECT placement_id FROM placements WHERE student_id=%s", (meera_id,))
    # Feedback is intentionally not inserted repeatedly; user can add it through the menu.
    print("Sample MySQL data and MongoDB skills inserted successfully.")
    print("Tip: use student IDs shown in the student list to test reports.")

if __name__ == "__main__":
    try:
        seed()
    except Exception as exc:
        print("Could not seed sample data:", exc)
        print("Check .env, MySQL schema setup, and MongoDB service.")
