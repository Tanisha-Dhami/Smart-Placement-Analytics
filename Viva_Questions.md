# ADBMS Viva Questions and Short Answers

1. **What is ADBMS?** Advanced Database Management Systems studies database design and advanced database features such as transactions, indexing, distributed data, and different database models.
2. **Why use MySQL here?** Student, course, marks, company, and placement records have structured relationships and constraints.
3. **Why use MongoDB?** Skills, certifications, projects, and interview histories can vary in length and structure.
4. **What is a primary key?** A column or group of columns that uniquely identifies a row.
5. **What is a foreign key?** A constraint that links a row to a valid row in another relational table.
6. **Can MySQL foreign keys directly reference MongoDB documents?** No. This project links records in Python using the shared `student_id`.
7. **What is a JOIN?** An SQL operation that combines rows from related tables.
8. **What is a VIEW?** A saved SQL query that can be queried like a virtual table.
9. **What is an index?** A data structure that can speed up lookups, with storage and write-performance trade-offs.
10. **What is a transaction?** A group of database operations treated as a unit; commit saves changes and rollback undoes uncommitted changes.
11. **What is MongoDB aggregation?** A pipeline that transforms and summarizes documents.
12. **What is a MongoDB document?** A BSON record made of fields and values, similar in concept to a JSON object.
13. **What is CRUD?** Create, Read, Update, Delete.
14. **How is SQL injection reduced?** The application uses parameterized SQL queries instead of string-concatenating user input into queries.
15. **How do you run the project?** Configure `.env`, run `schema.sql`, start MongoDB, install requirements, run `python seed_data.py`, then `python main.py`.
