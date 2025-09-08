
from pymongo import MongoClient
from config import settings

client = MongoClient(settings.mongodb_url)
db = client["tourist_safety"]
