# Smart Placement & Career Analytics System

A beginner-friendly ADBMS project using **Python + MySQL + MongoDB**. It is a terminal application; no Flask, React, or web server is required.

## What each database stores
- **MySQL:** students, courses, marks, companies, placement records.
- **MongoDB:** flexible student skills/certifications/projects and multiple interview feedback documents.
- Python combines data from both databases for a single student report.

## Software needed
1. Python 3.10 or newer
2. MySQL Server 8.x and MySQL Workbench (Workbench is a client; the MySQL Server service must also be installed/running)
3. MongoDB Community Server running locally. MongoDB Compass is optional.
4. VS Code (recommended)

## Step 1 — Open the project
Extract the ZIP. In VS Code, open the `Smart_Placement_Analytics` folder.

## Step 2 — Create a virtual environment (PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
If PowerShell blocks activation, run this for the current terminal only:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Step 3 — Configure environment
Copy `.env.example` to `.env` in the same folder. In VS Code PowerShell:
```powershell
Copy-Item .env.example .env
```
Open `.env` and replace `MYSQL_PASSWORD` with your MySQL password. If your MySQL username differs from `root`, update `MYSQL_USER`. Do not share your `.env` file.

## Step 4 — Create MySQL database and tables
Open MySQL Workbench and connect to your local MySQL Server. Open `schema.sql` and execute the whole script (lightning bolt). Confirm that `smart_placement_db` appears in the schemas panel.
The script creates tables, indexes, and the `student_average_marks` view.

## Step 5 — Start MongoDB
Make sure MongoDB Community Server is installed and running. The default URI is `mongodb://localhost:27017/`. If your MongoDB setup uses a different URI, change `MONGO_URI` in `.env`.

## Step 6 — Insert sample data
In the activated VS Code terminal:
```powershell
python seed_data.py
```
This adds a few example students, courses, marks, companies, placements, and MongoDB skills. It is designed to avoid duplicating most sample MySQL records when run more than once.

## Step 7 — Run the app
```powershell
python main.py
```
Choose a number from the menu. First choose `2` to view student IDs, then use those IDs for marks, skills, feedback, and reports.

## Test the key features
- Option 2: view sample students.
- Option 5: add skills to MongoDB for a student ID.
- Option 6: add interview feedback.
- Option 7: view the combined report from MySQL and MongoDB.
- Option 8: show placement summary and popular skills (MongoDB aggregation).
- Option 10: show averages from the SQL VIEW.

## ADBMS concepts included
- DDL: `CREATE DATABASE`, `CREATE TABLE`, `CREATE VIEW`, `CREATE INDEX`
- DML: `INSERT`, `UPDATE` (MongoDB upsert), `DELETE` (SQL foreign-key cascade is demonstrated by schema)
- SQL queries with parameters, joins, `GROUP BY`, aggregate functions, and a view
- Foreign keys and constraints
- Transaction commit/rollback in `mysql_db.py` via `execute_transaction`
- MongoDB documents and arrays, CRUD, indexes, and aggregation pipeline
- Application-level integration using `student_id`

## Common problems
- **Access denied for MySQL:** check `MYSQL_USER` and `MYSQL_PASSWORD` in `.env`.
- **Unknown database:** run `schema.sql` in MySQL Workbench before starting the app.
- **Can't connect to MySQL:** confirm the MySQL Server service is running; Workbench alone is not the server.
- **MongoDB connection refused:** confirm MongoDB Community Server is installed and running.
- **Module not found:** activate `.venv` and run `pip install -r requirements.txt`.
- **Duplicate email/course/marks:** sample rows may already exist; use a different email or course/semester combination.

## Important notes
- MySQL and MongoDB do not share foreign keys. The app uses the same `student_id` value to link records in Python.
- This project has not been tested against your personal laptop configuration. Database login settings and services must be configured locally.


## Deploy as a live web application (Streamlit)

This project includes `app.py`, a Streamlit web interface for the existing MySQL + MongoDB application.

### Before deployment
1. Create a cloud MySQL-compatible database (for example, TiDB Cloud) and run `schema.sql` against it.
2. Create a MongoDB Atlas cluster and database named `smart_placement_db`.
3. Update the database connection values in the Streamlit Community Cloud app's **Settings → Secrets**. Use TOML format:

```toml
MYSQL_HOST = "your-cloud-mysql-host"
MYSQL_PORT = "4000"
MYSQL_USER = "your-cloud-mysql-user"
MYSQL_PASSWORD = "your-cloud-mysql-password"
MYSQL_DATABASE = "smart_placement_db"
MYSQL_SSL_CA = ""

MONGO_URI = "mongodb+srv://your-user:your-password@your-cluster.mongodb.net/?retryWrites=true&w=majority"
MONGO_DATABASE = "smart_placement_db"
```

Use the exact host, port, username, password, and TLS settings supplied by your database providers. Do not commit passwords or `.env` files to GitHub.

### Run locally
```powershell
pip install -r requirements.txt
streamlit run app.py
```

### Deploy
1. Push this project folder to a GitHub repository.
2. In Streamlit Community Cloud, create a new app and select the repository.
3. Set the main file path to `app.py`.
4. Add the cloud database settings under app Secrets.
5. Deploy. The live URL will be provided by Streamlit Community Cloud.

The original command-line app remains available as `main.py`.
