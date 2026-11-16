from mysql_db import query_all
from mongodb_db import get_skills, get_feedback

def student_combined_report(student_id):
    students = query_all("SELECT student_id, name, email, department, semester FROM students WHERE student_id=%s", (student_id,))
    if not students:
        return None
    student = students[0]
    student["marks"] = query_all(
        """SELECT c.course_name, m.marks, m.semester
           FROM marks m JOIN courses c ON m.course_id=c.course_id
           WHERE m.student_id=%s ORDER BY m.semester, c.course_name""", (student_id,))
    student["placements"] = query_all(
        """SELECT co.company_name, p.job_role, p.package_lpa, p.status, p.placement_date
           FROM placements p JOIN companies co ON p.company_id=co.company_id
           WHERE p.student_id=%s ORDER BY p.placement_id DESC""", (student_id,))
    student["skills"] = get_skills(student_id)
    student["feedback"] = get_feedback(student_id)
    return student

def placement_summary():
    return query_all(
        """SELECT COUNT(*) AS total_records,
                  SUM(status='Selected') AS selected_count,
                  ROUND(AVG(CASE WHEN status='Selected' THEN package_lpa END), 2) AS average_selected_package_lpa
           FROM placements""")
