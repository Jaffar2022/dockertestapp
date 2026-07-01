from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv
import os

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

load_dotenv()

DB_URL = os.getenv("DB_URL")
DB_NAME = os.getenv("DB_NAME")

if not DB_URL:
    raise ValueError("❌ DB_URL not found in .env")

if not DB_NAME:
    raise ValueError("❌ DB_NAME not found in .env")

# --------------------------------------------------
# MongoDB Connection
# --------------------------------------------------

try:
    client = MongoClient(DB_URL, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    print("✅ Connected to MongoDB")
except Exception as e:
    print("❌ MongoDB Connection Failed")
    print(e)
    raise

db = client[DB_NAME]
users = db.users

# --------------------------------------------------
# FastAPI App
# --------------------------------------------------

app = FastAPI(title="User Management API")

# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://188.40.180.113:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Pydantic Model
# --------------------------------------------------

class User(BaseModel):
    name: str
    age: Optional[int] = None


# --------------------------------------------------
# Home
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "🚀 FastAPI Backend Running Successfully"
    }


# --------------------------------------------------
# Get All Users
# --------------------------------------------------

@app.get("/users")
def get_users():

    result = []

    for user in users.find():
        user["_id"] = str(user["_id"])
        result.append(user)

    return result


# --------------------------------------------------
# Get User By ID
# --------------------------------------------------

@app.get("/users/{user_id}")
def get_user(user_id: str):

    try:
        obj_id = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid User ID")

    user = users.find_one({"_id": obj_id})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user["_id"] = str(user["_id"])

    return user


# --------------------------------------------------
# Create User
# --------------------------------------------------

@app.post("/users", status_code=201)
def create_user(user: User):

    user_dict = user.model_dump(exclude_none=True)

    result = users.insert_one(user_dict)

    user_dict["_id"] = str(result.inserted_id)

    return user_dict


# --------------------------------------------------
# Update User
# --------------------------------------------------

@app.put("/users/{user_id}")
def update_user(user_id: str, user: User):

    try:
        obj_id = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid User ID")

    result = users.update_one(
        {"_id": obj_id},
        {
            "$set": user.model_dump(exclude_none=True)
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = users.find_one({"_id": obj_id})
    updated_user["_id"] = str(updated_user["_id"])

    return updated_user


# --------------------------------------------------
# Delete User
# --------------------------------------------------

@app.delete("/users/{user_id}")
def delete_user(user_id: str):

    try:
        obj_id = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid User ID")

    result = users.delete_one({"_id": obj_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "✅ User Deleted Successfully"
    }