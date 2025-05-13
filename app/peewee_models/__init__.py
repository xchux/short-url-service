import os

from dotenv import load_dotenv
from peewee import MySQLDatabase

load_dotenv()


db = MySQLDatabase(
    os.getenv("DB_SCHEMA", "shorturl"),
    host=os.getenv("DB_HOST", "shorturl"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    port=int(os.getenv("DB_POET", 3306)),
)
