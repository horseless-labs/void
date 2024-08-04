# This is for a Mongo database

import pymongo

url = "mongodb://localhost:27017/"
client = pymongo.MongoClient(url)

db = client['ueg_mongo']