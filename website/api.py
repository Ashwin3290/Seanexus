from flask_restful import Api, Resource
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from datetime import datetime
from bson import Binary,ObjectId
import io
import base64
import uuid


app = Flask((__name__))
CORS(app)
api=Api(app) 

client = MongoClient("mongodb://localhost:27017")  
db = client["seanexus"]  
user_data=db["user_data"]
app.config['dataset_collection'] = db["dataset"]
app.config['model_collection'] = db["model"]
app.config['user_data'] = db["user_data"]



class Login(Resource):
    def post(self):
        user_data = request.get_json()
        email = user_data.get('email')
        password = user_data.get('password')

        # Check if user_id and pass word are valid
        # Save user data to MongoDB
        if validate_credentials(email, password):  
            return {'message': 'Login successful'}, 200
        else:
            return {'message': 'Invalid credentials'}, 401



def validate_credentials(email, password):
    # Retrieve the user data from the database based on the user_id
    user = user_data.find_one({'email': email})

    # Check if the user exists and the password matches
    if user and user['password'] == password:
        return True
    else:
        return False
    

class Signup(Resource):
    def post(self):
        signup_data = request.get_json()
        name = signup_data.get('name')
        email = signup_data.get('email')
        password = signup_data.get('password')
        print(signup_data)

        # Check if email already exists in the database
        if check_email_exists(email):
            return {'message': 'Email already exists'}, 400

        # Save user data to MongoDB

        user_id=save_user_data(name, email,password)

        # Return success response
        return {'message': 'Signup successful',"user_id":user_id}, 200
    
def check_email_exists( email):
    # Check if email exists in the database
    existing_user = user_data.find_one({'email': email})
    return existing_user is not None

def save_user_data(name, email,password):
    # Save user data to MongoDB
    user_id = str(uuid.uuid4())
    signup_data = {'user_id': user_id, 'email': email, 'password': password, 'name': name}
    user_data.insert_one(signup_data)    

api.add_resource(Login, "/login")
api.add_resource(Signup, "/signup")

if __name__ == '__main__':
    app.run(debug=True)