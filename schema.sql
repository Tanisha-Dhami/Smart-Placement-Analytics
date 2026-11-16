CREATE DATABASE IF NOT EXISTS smart_placement_db;
USE smart_placement_db;

CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    department VARCHAR(80) NOT NULL,
    semester INT NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(120) NOT NULL UNIQUE,
    credits INT NOT NULL DEFAULT 3
);

CREATE TABLE IF NOT EXISTS marks (
    mark_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    marks DECIMAL(5,2) NOT NULL,
    semester INT NOT NULL,
    CONSTRAINT fk_marks_student FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    CONSTRAINT fk_marks_course FOREIGN KEY (course_id) REFERENCES courses(course_id),
    CONSTRAINT chk_marks_range CHECK (marks >= 0 AND marks <= 100),
    UNIQUE KEY uq_student_course_semester (student_id, course_id, semester)
);

CREATE TABLE IF NOT EXISTS companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(120) NOT NULL UNIQUE,
    industry VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS placements (
    placement_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    company_id INT NOT NULL,
    job_role VARCHAR(120) NOT NULL,
    package_lpa DECIMAL(8,2),
    status ENUM('Applied','Interview','Selected','Rejected') NOT NULL DEFAULT 'Applied',
    placement_date DATE,
    CONSTRAINT fk_placements_student FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    CONSTRAINT fk_placements_company FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE INDEX idx_students_department ON students(department);
CREATE INDEX idx_marks_student ON marks(student_id);
CREATE INDEX idx_placements_status ON placements(status);

CREATE OR REPLACE VIEW student_average_marks AS
SELECT s.student_id, s.name, s.department,
       ROUND(AVG(m.marks), 2) AS average_marks,
       COUNT(m.mark_id) AS subjects_recorded
FROM students s
LEFT JOIN marks m ON s.student_id = m.student_id
GROUP BY s.student_id, s.name, s.department;
