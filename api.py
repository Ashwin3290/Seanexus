from flask import Flask, request, jsonify, send_file
from fabric_cli import register_user, enroll_user, invoke_chaincode
import subprocess
from flask_restful import Api, Resource
import json
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from datetime import datetime
import io
import base64
import uuid
import qrcode
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode
import re

app = Flask((__name__))
api=Api(app) 

client = MongoClient("mongodb://localhost:27017")  
db = client["seanexus"]  
user_data=db["user_data"]
transactions=db["transaction"]

def check_transaction_exists_in_network(transaction_id):
    _,error = invoke_chaincode("queryData", transaction_id)
    if error:
        return True
    return False

def generate_unique_transaction_id():
    transaction_id = str(uuid.uuid4())
    if not check_transaction_exists_in_network(transaction_id):
        return generate_unique_transaction_id()
    else:
        return transaction_id
    
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
    user = user_data.find_one({'email': email})
    if user and user['password'] == password:
        return True
    else:
        return False
    
def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_bytes_io = BytesIO()
    img.save(img_bytes_io, format='PNG')
    img_bytes_io.seek(0)
    
    return img_bytes_io


def clean(data):
    return json.loads(data)

class Signup(Resource):
    def post(self):
        signup_data = request.get_json()
        name = signup_data.get('name')
        email = signup_data.get('email')
        password = signup_data.get('password')
        if check_email_exists(email):
            return {'message': 'Email already exists'}, 400


        user_id=save_user_data(name, email,password)

        return {'message': 'Signup successful',"user_id":user_id}, 200
    
def check_email_exists( email):
    existing_user = user_data.find_one({'email': email})
    return existing_user is not None

def save_user_data(name, email,password):
    user_id = str(uuid.uuid4())
    signup_data = {'user_id': user_id, 'email': email, 'password': password, 'name': name}
    user_data.insert_one(signup_data)    

api.add_resource(Login, "/login")
api.add_resource(Signup, "/signup")

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    try:
        enroll_user(username, password)
        register_user(username, password)
        return jsonify({'message': 'User registered and enrolled successfully'}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/invoke', methods=['POST'])
def push_data():
    function = request.json.get('function')
    args = request.json.get('args', [])
    if not function:
        return jsonify({'error': 'Function and username are required'}), 400

    try:
        timestamp = str(datetime.now().isoformat())
        transaction_id = generate_unique_transaction_id()
        _,error=invoke_chaincode(function, transaction_id,args[0], args[1], args[2], timestamp)
        if error:
            return jsonify({'error': error}), 500
        if transaction_id:
            transactions.insert_one({'transaction_id': transaction_id, 'function': function, 'args': args, 'timestamp':timestamp })
        qrcode=generate_qr_code(transaction_id)
        return send_file(qrcode, mimetype='image/png'), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/query', methods=['GET'])
def query():
    function = request.json.get('function')
    args = request.json.get('args', [])
    if not function:
        return jsonify({'error': 'Function and transactionid are required'}), 400

    try:
        result,error = invoke_chaincode(function, args[0])
        if error:
            return jsonify({'error': error}), 500
        return jsonify({'result':eval(result[1:])}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500



@app.route('/decode_qr_code', methods=['POST'])
def decode_qr_code():
    qr_image = request.files['qr_image']
    if not qr_image:
        return jsonify({'error': 'No QR image uploaded'}), 400

    decoded_objects = decode(Image.open(qr_image))
    if decoded_objects:
        decoded_data = decoded_objects[0].data.decode('utf-8')
        function = "queryData"
        if not function:
            return jsonify({'error': 'Function and transactionid are required'}), 400

        try:
            result,error = invoke_chaincode(function, decoded_data)
            if error:
                return jsonify({'error': error}), 500
            return jsonify({'result': clean(result)}), 200
        except subprocess.CalledProcessError as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)