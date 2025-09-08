import certifi
from pymongo import MongoClient
from config import settings

client = MongoClient(settings.mongodb_url, tlsCAFile=certifi.where())
db = client[settings.mongo_db_name]
