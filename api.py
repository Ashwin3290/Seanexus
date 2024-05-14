from flask import Flask, request, jsonify, send_file
from fabric_cli import register_user, enroll_user, invoke_chaincode
import subprocess
from flask_restful import Api, Resource
import json
from pymongo import MongoClient
from datetime import datetime
import io
import uuid
import qrcode
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode
import requests
from flask_cors import CORS
import random

app = Flask((__name__))
api=Api(app) 
CORS(app)

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
        status,user_id = validate_credentials(email, password)
        if status:  
            return {'message': 'Login successful',"vendor_id":user_id}, 200
        else:
            return {'message': 'Invalid credentials'}, 401



def validate_credentials(email, password):
    user = user_data.find_one({'email': email})
    if user and user['password'] == password:
        return True,user['user_id']
    else:
        return False,None
    
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
    user_id = str(random.randint(1000, 999999))
    signup_data = {'user_id': user_id, 'email': email, 'password': password, 'name': name}
    user_data.insert_one(signup_data)    

api.add_resource(Login, "/login")
api.add_resource(Signup, "/signup")

# @app.route('/register', methods=['POST'])
# def register():
#     username = request.json.get('username')
#     password = request.json.get('password')
#     if not username or not password:
#         return jsonify({'error': 'Username and password are required'}), 400

#     try:
#         enroll_user(username, password)
#         register_user(username, password)
#         return jsonify({'message': 'User registered and enrolled successfully'}), 200
#     except subprocess.CalledProcessError as e:
#         return jsonify({'error': str(e)}), 500

@app.route('/invoke', methods=['POST', 'OPTIONS'])
def push_data():
        
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'Preflight request handled successfully'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response

    if request.method == 'POST':
        function = request.json.get('function')


        args = request.json.get('args', [])
        if not function:
            return jsonify({'error': 'Function and username are required'}), 400

        try:
            timestamp = str(datetime.now().isoformat())
            # transaction_id = generate_unique_transaction_id()
            transaction_id= str(uuid.uuid4())
            freegeoip_url = f"http://freegeoip.app/json/{args[2]}"
            response = requests.get(freegeoip_url)
            print(response)
            # geolocation_data = response.json()

            _, error = invoke_chaincode(function, transaction_id, args[0], args[1], args[2], timestamp)
            if error:
                return jsonify({'error': error}), 500

            if transaction_id:
                qr_code_image = generate_qr_code(transaction_id)
                transactions.update_one(
                    {'transaction_id': transaction_id},
                    {'$set': {'qr_code': qr_code_image.getvalue()}}
                )

            return jsonify({'message': 'Transaction completed successfully'}), 200
        
        except subprocess.CalledProcessError as e:
            return jsonify({'error': str(e)}), 500

# New endpoint to serve QR code image based on transaction ID
@app.route('/qr_code/<transaction_id>', methods=['GET'])
def get_qr_code(transaction_id):
    # Fetch QR code data from the transactions table
    transaction = transactions.find_one({'transaction_id': transaction_id})
    if transaction and 'qr_code' in transaction:
        # Serve QR code image
        qr_code_image = BytesIO(transaction['qr_code'])
        return send_file(qr_code_image, mimetype='image/png'), 200
    else:
        return jsonify({'error': 'QR code not found'}), 404

@app.route('/query', methods=['POST'])
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
    app.run(port=5000, debug=True)