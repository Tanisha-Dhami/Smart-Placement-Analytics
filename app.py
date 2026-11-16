import os
import streamlit as st

# Streamlit Community Cloud stores deployment variables in st.secrets.
# Copy them into environment variables so the existing DB modules can use them.
try:
    for key, value in st.secrets.items():
        if not isinstance(value, dict):
            os.environ[str(key)] = str(value)
except Exception:
    pass

from mysql_db import query_all, execute
from mongodb_db import save_skills, add_feedback, get_skills, get_feedback, find_students_by_skill, popular_skills
from analytics import student_combined_report, placement_summary

st.set_page_config(page_title="Smart Placement & Career Analytics", page_icon="🎓", layout="wide")

st.title("🎓 Smart Placement & Career Analytics System")
st.caption("A student placement management application powered by MySQL and MongoDB.")

def show_error(err):
    st.error(f"Operation failed: {err}")
    st.info("Check that the cloud database credentials are configured in Streamlit Secrets and that schema.sql has been executed.")

def students():
    return query_all("SELECT student_id, name, email, department, semester FROM students ORDER BY student_id")

def student_options():
    rows = students()
    return {f'{r["student_id"]} — {r["name"]} ({r["department"]})': r["student_id"] for r in rows}

action = st.sidebar.selectbox(
    "Choose a feature",
    [
        "Dashboard",
        "Add Student",
        "View Students",
        "Record Course Marks",
        "Add Placement Record",
        "Manage Skills (MongoDB)",
        "Add Interview Feedback",
        "Combined Student Report",
        "Placement & Skills Analytics",
        "Search Students by Skill",
        "Average Marks Report",
    ],
)

try:
    if action == "Dashboard":
        try:
            s = query_all("SELECT COUNT(*) AS n FROM students")[0]["n"]
            p = placement_summary()[0]
            c1, c2, c3 = st.columns(3)
            c1.metric("Registered students", s or 0)
            c2.metric("Placement records", p["total_records"] or 0)
            c3.metric("Selected students", p["selected_count"] or 0)
            st.subheader("About this project")
            st.write("This application stores structured student, academic and placement data in MySQL, while technical skills, certifications, projects and interview feedback are stored in MongoDB.")
            st.success("Database connection successful.")
        except Exception as e:
            show_error(e)

    elif action == "Add Student":
        with st.form("add_student"):
            name = st.text_input("Full name")
            email = st.text_input("Email")
            department = st.text_input("Department", value="CSE")
            semester = st.number_input("Semester", min_value=1, max_value=8, value=5)
            submitted = st.form_submit_button("Add student")
        if submitted:
            try:
                sid = execute("INSERT INTO students(name,email,department,semester) VALUES(%s,%s,%s,%s)", (name.strip(), email.strip(), department.strip(), int(semester)))
                st.success(f"Student added successfully. Student ID: {sid}")
            except Exception as e:
                show_error(e)

    elif action == "View Students":
        st.subheader("Registered Students")
        st.dataframe(students(), use_container_width=True, hide_index=True)

    elif action == "Record Course Marks":
        opts = student_options()
        if not opts:
            st.warning("Add a student first.")
        else:
            with st.form("marks"):
                sid_label = st.selectbox("Student", list(opts))
                course = st.text_input("Course name")
                marks = st.number_input("Marks", min_value=0.0, max_value=100.0, value=75.0)
                semester = st.number_input("Semester", min_value=1, max_value=8, value=5)
                credits = st.number_input("Credits (used only if course is new)", min_value=1, max_value=6, value=3)
                submitted = st.form_submit_button("Save marks")
            if submitted:
                try:
                    sid = opts[sid_label]
                    found = query_all("SELECT course_id FROM courses WHERE course_name=%s", (course.strip(),))
                    cid = found[0]["course_id"] if found else execute("INSERT INTO courses(course_name,credits) VALUES(%s,%s)", (course.strip(), int(credits)))
                    execute("INSERT INTO marks(student_id,course_id,marks,semester) VALUES(%s,%s,%s,%s)", (sid,cid,float(marks),int(semester)))
                    st.success("Course marks saved.")
                except Exception as e:
                    show_error(e)

    elif action == "Add Placement Record":
        opts = student_options()
        if not opts:
            st.warning("Add a student first.")
        else:
            with st.form("placement"):
                sid_label = st.selectbox("Student", list(opts))
                company = st.text_input("Company name")
                industry = st.text_input("Industry")
                role = st.text_input("Job role")
                package = st.number_input("Package in LPA (0 if unknown)", min_value=0.0, value=0.0)
                status = st.selectbox("Application status", ["Applied", "Interview", "Selected", "Rejected"])
                submitted = st.form_submit_button("Save placement")
            if submitted:
                try:
                    found = query_all("SELECT company_id FROM companies WHERE company_name=%s", (company.strip(),))
                    cid = found[0]["company_id"] if found else execute("INSERT INTO companies(company_name,industry) VALUES(%s,%s)", (company.strip(),industry.strip()))
                    execute("INSERT INTO placements(student_id,company_id,job_role,package_lpa,status,placement_date) VALUES(%s,%s,%s,%s,%s,CURDATE())", (opts[sid_label],cid,role.strip(),package if package > 0 else None,status))
                    st.success("Placement record saved.")
                except Exception as e:
                    show_error(e)

    elif action == "Manage Skills (MongoDB)":
        opts = student_options()
        if not opts:
            st.warning("Add a student first.")
        else:
            with st.form("skills"):
                sid_label = st.selectbox("Student", list(opts))
                skills = st.text_input("Skills (comma-separated)", placeholder="Python, SQL, Machine Learning")
                certs = st.text_input("Certifications (comma-separated)")
                projects = st.text_input("Projects (comma-separated)")
                submitted = st.form_submit_button("Save skills profile")
            if submitted:
                try:
                    save_skills(opts[sid_label], skills, certs, projects)
                    st.success("Skills profile saved in MongoDB.")
                except Exception as e:
                    show_error(e)

    elif action == "Add Interview Feedback":
        opts = student_options()
        if not opts:
            st.warning("Add a student first.")
        else:
            with st.form("feedback"):
                sid_label = st.selectbox("Student", list(opts))
                company = st.text_input("Company")
                round_name = st.selectbox("Interview round", ["Technical", "HR", "Aptitude", "Managerial", "Other"])
                feedback = st.text_area("Feedback")
                rating = st.slider("Rating", 1, 5, 4)
                submitted = st.form_submit_button("Save feedback")
            if submitted:
                try:
                    add_feedback(opts[sid_label], company.strip(), round_name, feedback.strip(), rating)
                    st.success("Interview feedback saved in MongoDB.")
                except Exception as e:
                    show_error(e)

    elif action == "Combined Student Report":
        opts = student_options()
        if not opts:
            st.warning("No students found.")
        else:
            label = st.selectbox("Select student", list(opts))
            if st.button("Generate report"):
                try:
                    r = student_combined_report(opts[label])
                    st.header(f'{r["name"]} — Student ID {r["student_id"]}')
                    a, b = st.columns(2)
                    with a:
                        st.subheader("Academic Records")
                        st.dataframe(r["marks"], use_container_width=True, hide_index=True)
                    with b:
                        st.subheader("Placement Records")
                        st.dataframe(r["placements"], use_container_width=True, hide_index=True)
                    st.subheader("MongoDB Skills Profile")
                    if r["skills"]:
                        st.write("**Skills:**", ", ".join(r["skills"].get("skills", [])) or "None")
                        st.write("**Certifications:**", ", ".join(r["skills"].get("certifications", [])) or "None")
                        st.write("**Projects:**", ", ".join(r["skills"].get("projects", [])) or "None")
                    else:
                        st.info("No skills profile available.")
                    st.subheader("Interview Feedback")
                    st.dataframe(r["feedback"], use_container_width=True, hide_index=True)
                except Exception as e:
                    show_error(e)

    elif action == "Placement & Skills Analytics":
        try:
            p = placement_summary()[0]
            a, b, c = st.columns(3)
            a.metric("Placement records", p["total_records"] or 0)
            b.metric("Selected records", p["selected_count"] or 0)
            c.metric("Average selected package (LPA)", p["average_selected_package_lpa"] or 0)
            st.subheader("Most Popular Skills")
            skills = popular_skills()
            if skills:
                st.bar_chart({x["_id"]: x["student_count"] for x in skills})
                st.dataframe([{"Skill": x["_id"], "Students": x["student_count"]} for x in skills], use_container_width=True, hide_index=True)
            else:
                st.info("No skill profiles found.")
        except Exception as e:
            show_error(e)

    elif action == "Search Students by Skill":
        skill = st.text_input("Enter a skill", placeholder="Python")
        if st.button("Search"):
            try:
                st.dataframe(find_students_by_skill(skill.strip()), use_container_width=True, hide_index=True)
            except Exception as e:
                show_error(e)

    elif action == "Average Marks Report":
        st.subheader("Student Average Marks (SQL VIEW)")
        try:
            rows = query_all("SELECT student_id, name, department, average_marks, subjects_recorded FROM student_average_marks ORDER BY average_marks DESC")
            st.dataframe(rows, use_container_width=True, hide_index=True)
        except Exception as e:
            show_error(e)

except Exception as e:
    show_error(e)

st.divider()
st.caption("Academic demonstration project • MySQL + MongoDB • Python + Streamlit")
