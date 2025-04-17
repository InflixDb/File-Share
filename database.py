# database.py
from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")  # Update this to your MongoDB URI if using MongoDB Atlas
db = client['file_share_bot']

# Mongo collections
users_collection = db['users']
admins_collection = db['admins']
filters_collection = db['filters']
config_collection = db['config']

# Add or get a user
def add_user(user_id, is_premium=False, is_subscribed=False):
    user_data = {
        "user_id": user_id,
        "is_premium": is_premium,
        "is_subscribed": is_subscribed,
    }
    users_collection.update_one({"user_id": user_id}, {"$set": user_data}, upsert=True)

def get_user(user_id):
    return users_collection.find_one({"user_id": user_id})

def update_subscription(user_id, is_subscribed):
    users_collection.update_one({"user_id": user_id}, {"$set": {"is_subscribed": is_subscribed}})

def get_admins():
    return [admin["user_id"] for admin in admins_collection.find()]

def add_admin(user_id):
    admins_collection.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

def remove_admin(user_id):
    admins_collection.delete_one({"user_id": user_id})

def add_filter(anime_name, link):
    filter_data = {
        "anime_name": anime_name,
        "link": link
    }
    filters_collection.update_one({"anime_name": anime_name}, {"$set": filter_data}, upsert=True)

def get_filter(anime_name):
    return filters_collection.find_one({"anime_name": anime_name})
