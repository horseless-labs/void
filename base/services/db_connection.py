# This is for a Mongo database

import pymongo
import os

# The environment variables for username and password are to be provided in the
# docker-compose.yml file.
# TODO: uncomment when containerized
# username = os.environ.get("MONGODB_USERNAME")
# password = os.environ.get("MONGODB_PASSWORD")
url = "mongodb://localhost:27017/"
client = pymongo.MongoClient(url)

db = client['chat_db']