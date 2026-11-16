import os
from datetime import datetime, timezone
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

load_dotenv()

def get_database():
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    name = os.getenv("MONGO_DATABASE", "smart_placement_db")
    client = MongoClient(uri, serverSelectionTimeoutMS=2500)
    # Force a connection check now so errors appear when the user selects a MongoDB feature.
    client.admin.command("ping")
    return client[name]

def ensure_indexes():
    db = get_database()
    db.student_skills.create_index([("student_id", ASCENDING)], unique=True)
    db.student_skills.create_index([("skills", ASCENDING)])
    db.interview_feedback.create_index([("student_id", ASCENDING)])
    return True

def save_skills(student_id, skills, certifications, projects):
    db = get_database()
    doc = {
        "student_id": int(student_id),
        "skills": [x.strip() for x in skills.split(",") if x.strip()],
        "certifications": [x.strip() for x in certifications.split(",") if x.strip()],
        "projects": [x.strip() for x in projects.split(",") if x.strip()],
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    db.student_skills.update_one({"student_id": int(student_id)}, {"$set": doc}, upsert=True)
    return doc

def add_feedback(student_id, company, round_name, feedback, rating):
    db = get_database()
    doc = {
        "student_id": int(student_id),
        "company_name": company,
        "round": round_name,
        "feedback": feedback,
        "rating": int(rating),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    db.interview_feedback.insert_one(doc)
    return doc

def get_skills(student_id):
    db = get_database()
    return db.student_skills.find_one({"student_id": int(student_id)}, {"_id": 0})

def get_feedback(student_id):
    db = get_database()
    return list(db.interview_feedback.find({"student_id": int(student_id)}, {"_id": 0}).sort("created_at", -1))

def find_students_by_skill(skill):
    db = get_database()
    return list(db.student_skills.find({"skills": {"$regex": f"^{skill}$", "$options": "i"}}, {"_id": 0}))

def popular_skills():
    db = get_database()
    pipeline = [
        {"$unwind": "$skills"},
        {"$group": {"_id": "$skills", "student_count": {"$sum": 1}}},
        {"$sort": {"student_count": -1, "_id": 1}},
        {"$limit": 10}
    ]
    return list(db.student_skills.aggregate(pipeline))
