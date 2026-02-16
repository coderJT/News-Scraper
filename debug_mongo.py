
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import sys

uri = "mongodb+srv://justin:REDACTED@products.a2ruu.mongodb.net/?appName=Products"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    print("Attempting to ping deployment...")
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Connection failed: {e}")
    # Print more specific details if possible
    if hasattr(e, 'details'):
        print(f"Error details: {e.details}")
