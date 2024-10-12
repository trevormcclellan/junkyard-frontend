from flask import Flask, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# MongoDB connection details
MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')
MONGO_COLLECTION_NAME_TEARAPART = os.getenv('MONGO_COLLECTION_NAME_TEARAPART')
MONGO_COLLECTION_NAME_UTPAP = os.getenv('MONGO_COLLECTION_NAME_UTPAP')
MONGO_COLLECTION_NAME_PULLNSAVE = os.getenv('MONGO_COLLECTION_NAME_PULLNSAVE')

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
collection_tearapart = db[MONGO_COLLECTION_NAME_TEARAPART]
collection_utpap = db[MONGO_COLLECTION_NAME_UTPAP]
collection_pullnsave = db[MONGO_COLLECTION_NAME_PULLNSAVE]

@app.route('/')
def index():
    # Fetch data from MongoDB collections
    cars_tearapart = list(collection_tearapart.find())
    cars_utpap = list(collection_utpap.find())
    cars_pullnsave = list(collection_pullnsave.find())
    
    return render_template('index.html', cars_tearapart=cars_tearapart, cars_utpap=cars_utpap, cars_pullnsave=cars_pullnsave)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
