"""
MongoDB storage operations for credentials and signatures
"""

from datetime import datetime
from pymongo import MongoClient
from .config import MONGODB_URI, DATABASE_NAME


def save_credentials(cookies: dict) -> str:
    """
    Save user credentials to MongoDB.
    Invalidates all existing credentials before saving new ones.
    
    Args:
        cookies: Dictionary of cookies from browser
        
    Returns:
        The user_id from cookies
    """
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    collection = db["credentials"]
    
    # Invalidate all existing credentials
    collection.update_many({}, {"$set": {"is_valid": False}})
    
    # Build user ID from cookie values
    user_id = "".join(cookies.get(k, "") for k in ["a1", "webId", "gid", "web_session"])
    
    # Prepare document
    doc = {
        "user_id": user_id,
        "cookies": cookies,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_valid": True
    }
    
    collection.insert_one(doc)
    client.close()
    
    return user_id


def invalidate_all_credentials() -> int:
    """
    Invalidate all stored credentials.
    
    Returns:
        Number of documents updated
    """
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    collection = db["credentials"]
    
    result = collection.update_many({}, {"$set": {"is_valid": False}})
    client.close()
    
    return result.modified_count
