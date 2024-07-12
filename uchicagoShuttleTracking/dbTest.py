from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from secrets import *
import mysql.connector

"""
# Create a new Mongo DB client and connect to the server
client = MongoClient(MONGO_DB_URL, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
"""

# Check local DB

try:
	cnx = mysql.connector.connect(
		user = DB_USER,
		password = DB_PASS,
		host = DB_HOST,
		database = DB_NAME
	)
	cnx.close()
	print("Successfully connected")
except Exception as e:
	print(e)
