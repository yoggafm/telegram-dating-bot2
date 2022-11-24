import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('5728932780:AAFQ-Hz0QAQHIV7j7s8hiH0n6Fj9adfKfhQ')
ADMIN = os.getenv('JualVIPVVIP').split(' ')  # add admin IDs separated by spaces in .env file

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
INVITE_LINK = os.getenv('INVITE_LINK')
