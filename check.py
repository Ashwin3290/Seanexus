import requests

# Define the base URL of your Flask API
base_url = "http://localhost:5000"

# Example data for login endpoint
login_data = {
    "email": "example@example.com",
    "password": "password123"
}

# Example data for signup endpoint
signup_data = {
    "name": "John Doe",
    "email": "johndoe@example.com",
    "password": "password123"
}

# Example data for register endpoint
register_data = {
    "username": "example_user",
    "password": "example_password"
}

# Example data for invoke endpoint
invoke_data = {
    "function": "example_function",
    "args": ["arg1", "arg2", "arg3"]
}

# Example data for query endpoint
query_data = {
    "function": "example_function",
    "args": ["example_arg"]
}

# Example data for decode_qr_code endpoint
files = {'qr_image': open('path_to_qr_image.png', 'rb')}

# Make a POST request to the login endpoint
response = requests.post(f"{base_url}/login", json=login_data)
print("Login Response:", response.json())

# Make a POST request to the signup endpoint
response = requests.post(f"{base_url}/signup", json=signup_data)
print("Signup Response:", response.json())

# Make a POST request to the register endpoint
response = requests.post(f"{base_url}/register", json=register_data)
print("Register Response:", response.json())

# Make a POST request to the invoke endpoint
response = requests.post(f"{base_url}/invoke", json=invoke_data)
print("Invoke Response:", response.text)

# Make a GET request to the query endpoint
response = requests.get(f"{base_url}/query", json=query_data)
print("Query Response:", response.json())

# Make a POST request to the decode_qr_code endpoint
response = requests.post(f"{base_url}/decode_qr_code", files=files)
print("Decode QR Code Response:", response.json())
