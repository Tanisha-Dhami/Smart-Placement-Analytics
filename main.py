from mysql_db import query_all, execute
from mongodb_db import save_skills, add_feedback, get_skills, get_feedback, find_students_by_skill, popular_skills
from analytics import student_combined_report, placement_summary

def line():
    print("-" * 64)

def show_students():
    rows = query_all("SELECT student_id, name, email, department, semester FROM students ORDER BY student_id")
    if not rows:
        print("No students found.")
    for r in rows:
        print(f'ID: {r["student_id"]} | {r["name"]} | {r["email"]} | {r["department"]} | Sem {r["semester"]}')

def add_student():
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    department = input("Department: ").strip()
    try:
        semester = int(input("Semester (1-8): "))
        if not name or not email or not department or not 1 <= semester <= 8:
            raise ValueError("Please enter valid non-empty details and semester 1-8.")
        sid = execute("INSERT INTO students(name,email,department,semester) VALUES(%s,%s,%s,%s)", (name,email,department,semester))
        print(f"Student added. Student ID = {sid}")
    except Exception as e:
        print("Could not add student:", e)

def add_course_marks():
    try:
        sid = int(input("Student ID: "))
        course_name = input("Course name: ").strip()
        marks = float(input("Marks (0-100): "))
        semester = int(input("Semester: "))
        if not 0 <= marks <= 100:
            raise ValueError("Marks must be between 0 and 100.")
        courses = query_all("SELECT course_id FROM courses WHERE course_name=%s", (course_name,))
        if not courses:
            credits = int(input("Course not found. Enter credits for new course (1-6): "))
            if not 1 <= credits <= 6:
                raise ValueError("Credits must be 1-6.")
            cid = execute("INSERT INTO courses(course_name,credits) VALUES(%s,%s)", (course_name,credits))
        else:
            cid = courses[0]["course_id"]
        execute("INSERT INTO marks(student_id,course_id,marks,semester) VALUES(%s,%s,%s,%s)", (sid,cid,marks,semester))
        print("Marks saved.")
    except Exception as e:
        print("Could not save marks:", e)

def add_company_placement():
    try:
        company = input("Company name: ").strip()
        industry = input("Industry: ").strip()
        rows = query_all("SELECT company_id FROM companies WHERE company_name=%s", (company,))
        if not rows:
            cid = execute("INSERT INTO companies(company_name,industry) VALUES(%s,%s)", (company,industry))
        else:
            cid = rows[0]["company_id"]
        sid = int(input("Student ID: "))
        role = input("Job role: ").strip()
        package_text = input("Package in LPA (leave blank if unknown): ").strip()
        package = float(package_text) if package_text else None
        status = input("Status [Applied/Interview/Selected/Rejected]: ").strip().title()
        if status not in ["Applied","Interview","Selected","Rejected"]:
            raise ValueError("Status must be Applied, Interview, Selected, or Rejected.")
        execute("INSERT INTO placements(student_id,company_id,job_role,package_lpa,status,placement_date) VALUES(%s,%s,%s,%s,%s,CURDATE())", (sid,cid,role,package,status))
        print("Placement record saved.")
    except Exception as e:
        print("Could not save placement:", e)

def manage_skills():
    try:
        sid = int(input("Student ID: "))
        skills = input("Skills, comma-separated: ")
        certs = input("Certifications, comma-separated: ")
        projects = input("Projects, comma-separated: ")
        save_skills(sid, skills, certs, projects)
        print("Skills profile saved in MongoDB.")
    except Exception as e:
        print("Could not save skills:", e)

def manage_feedback():
    try:
        sid = int(input("Student ID: "))
        company = input("Company: ").strip()
        round_name = input("Interview round (e.g., Technical): ").strip()
        feedback = input("Feedback: ").strip()
        rating = int(input("Rating (1-5): "))
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be from 1 to 5.")
        add_feedback(sid, company, round_name, feedback, rating)
        print("Interview feedback saved in MongoDB.")
    except Exception as e:
        print("Could not save feedback:", e)

def show_student_report():
    try:
        sid = int(input("Student ID: "))
        report = student_combined_report(sid)
        if not report:
            print("No student found with that ID.")
            return
        line()
        print(f'{report["name"]} (ID {report["student_id"]})')
        print(f'Email: {report["email"]} | Department: {report["department"]} | Semester: {report["semester"]}')
        print("\nACADEMIC RECORDS")
        if report["marks"]:
            for m in report["marks"]:
                print(f'  {m["course_name"]}: {m["marks"]}/100 (semester {m["semester"]})')
        else: print("  No marks recorded.")
        print("\nPLACEMENT RECORDS")
        if report["placements"]:
            for p in report["placements"]:
                print(f'  {p["company_name"]} | {p["job_role"]} | {p["status"]} | Package: {p["package_lpa"]} LPA')
        else: print("  No placement records.")
        print("\nMONGODB SKILLS PROFILE")
        if report["skills"]:
            for key in ["skills","certifications","projects"]:
                print(f'  {key.title()}: {", ".join(report["skills"].get(key, [])) or "None"}')
        else: print("  No skills profile.")
        print("\nINTERVIEW FEEDBACK")
        if report["feedback"]:
            for f in report["feedback"]:
                print(f'  {f["company_name"]} | {f["round"]} | Rating {f["rating"]}/5 | {f["feedback"]}')
        else: print("  No interview feedback.")
        line()
    except Exception as e:
        print("Could not generate report:", e)

def show_analytics():
    try:
        summary = placement_summary()[0]
        print("PLACEMENT SUMMARY")
        print(f'Total placement records: {summary["total_records"] or 0}')
        print(f'Selected records: {summary["selected_count"] or 0}')
        print(f'Average selected package: {summary["average_selected_package_lpa"] or 0} LPA')
        print("\nTOP SKILLS (MongoDB aggregation)")
        skills = popular_skills()
        if not skills: print("No skill profiles found.")
        for s in skills:
            print(f'  {s["_id"]}: {s["student_count"]} student(s)')
    except Exception as e:
        print("Could not generate analytics:", e)

def search_skill():
    try:
        skill = input("Enter skill to search (e.g., Python): ").strip()
        results = find_students_by_skill(skill)
        if not results: print("No student profiles found for that skill.")
        for r in results:
            print(f'Student ID {r["student_id"]}: {", ".join(r.get("skills", []))}')
    except Exception as e:
        print("Could not search skill:", e)

def show_average_marks():
    try:
        rows = query_all("SELECT student_id, name, department, average_marks, subjects_recorded FROM student_average_marks ORDER BY average_marks DESC")
        for r in rows:
            print(f'ID {r["student_id"]} | {r["name"]} | {r["department"]} | Average: {r["average_marks"]} | Subjects: {r["subjects_recorded"]}')
    except Exception as e:
        print("Could not show marks report. Run schema.sql first:", e)

def main():
    while True:
        line()
        print("SMART PLACEMENT & CAREER ANALYTICS SYSTEM")
        line()
        print("1. Add student")
        print("2. View students")
        print("3. Add course marks")
        print("4. Add company placement record")
        print("5. Add/update student skills (MongoDB)")
        print("6. Add interview feedback (MongoDB)")
        print("7. Generate combined student report")
        print("8. Placement and popular skills analytics")
        print("9. Search students by skill")
        print("10. Student average marks report (SQL VIEW)")
        print("0. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1": add_student()
        elif choice == "2":
            try: show_students()
            except Exception as e: print("Could not load students:", e)
        elif choice == "3": add_course_marks()
        elif choice == "4": add_company_placement()
        elif choice == "5": manage_skills()
        elif choice == "6": manage_feedback()
        elif choice == "7": show_student_report()
        elif choice == "8": show_analytics()
        elif choice == "9": search_skill()
        elif choice == "10": show_average_marks()
        elif choice == "0":
            print("Goodbye!")
            break
        else: print("Invalid choice. Enter a number from the menu.")

if __name__ == "__main__":
    main()
