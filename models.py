from config import Config
from flask import Flask
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)
mongo = PyMongo(app)

class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
    
    def save(self):
        user = {
            'username': self.username,
            'email': self.email,
            'password': self.password
        }
        mongo.db.users.insert_one(user)

    @staticmethod
    def find_by_email(email):
        return mongo.db.users.find_one({'email': email})
    
    @staticmethod
    def check_password(stored_password, provided_password):
        return check_password_hash(stored_password, provided_password)

class Event:
    def __init__(self, title, description, date, time, location, price, organizer_id):
        self.title = title
        self.description = description
        self.date = date
        self.time = time
        self.location = location
        self.price = price
        self.organizer_id = organizer_id

    def save(self):
        event = {
            'title': self.title,
            'description': self.description,
            'date': self.date,
            'time': self.time,
            'location': self.location,
            'price': self.price,
            'organizer_id': self.organizer_id
        }
        mongo.db.events.insert_one(event)

    @staticmethod
    def find_by_organizer(organizer_id):
        return mongo.db.events.find({'organizer_id': organizer_id})
