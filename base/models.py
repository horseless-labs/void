from django.db import models
from .services.db_connection import db

# Create your models here.
person_collection = db['Person']
chat_collection = db["conversation"]