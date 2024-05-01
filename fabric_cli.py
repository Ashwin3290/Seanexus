import subprocess
import os
import json

# Set the necessary environment variables
os.environ['FABRIC_CFG_PATH'] = "fabric/config"
os.environ['CORE_PEER_LOCALMSPID'] = "Org1MSP"

# Paths and configurations
FABRIC_CA_CLIENT = "fabric-ca-client"
PEER_BINARY = "peer"
ORDERER_ADDRESS = "orderer.example.com:7050"
CHANNEL_NAME = "mychannel"
CHAINCODE_NAME = "fishing_network"
ORG1_MSP_PATH = "/home/ashwin/Hyperledger/seanexus/artifacts/channel/crypto-config/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp"
ORG2_MSP_PATH = "/home/ashwin/Hyperledger/seanexus/artifacts/channel/crypto-config/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp"
ORDERER_TLS_CERT = "/home/ashwin/Hyperledger/seanexus/artifacts/channel/crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/tls/ca.crt"

FABRIC_CA_CLIENT = "fabric-ca-client"
CA_NAME = "ca-org1"  
CA_CERT_FILE = "/home/ashwin/Hyperledger/seanexus/artifacts/channel/crypto-config/peerOrganizations/org1.example.com/ca/ca.org1.example.com-cert.pem"

def enroll_admin(admin_name, admin_password):
    msp_path = ORG1_MSP_PATH
    ca_server_hostname = "ca.org1.example.com:7054" 
    command = f"{FABRIC_CA_CLIENT} enroll -u https://{admin_name}:{admin_password}@{ca_server_hostname} --caname {CA_NAME} -M {msp_path} --tls.certfiles {CA_CERT_FILE}"
    subprocess.run(command, shell=True, check=True)

def register_user(username, password):
    command = f"{FABRIC_CA_CLIENT} register --caname {CA_NAME} --id.name {username} --id.secret {password} --id.type client --tls.certfiles {CA_CERT_FILE}"
    subprocess.run(command, shell=True, check=True)

def enroll_user(username, password):
    msp_path = f"artifacts/channel/crypto-config/peerOrganizations/org1.example.com/users/{username}@org1.example.com/msp"
    ca_server_hostname = "0.0.0.0:7054"
    command = f"{FABRIC_CA_CLIENT} enroll -u https://{username}:{password}@{ca_server_hostname} --caname {CA_NAME} -M {msp_path} --tls.certfiles {CA_CERT_FILE}"
    subprocess.run(command, shell=True, check=True)


def invoke_chaincode(function_name, *args):
    # Construct the command to call the Bash script
    command = ['./invoke.sh', function_name, *map(str, args)]
    
    # Run the command and capture the output
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        result = output.decode()
        start_index = result.find('payload:') + len('payload:')
        end_index = result.rfind('"')
        data_part = result[start_index:end_index]
        clean_data_part = data_part.replace('\\"', '"').replace("\\n", "").strip()
        return clean_data_part, None

    except subprocess.CalledProcessError as e:
        error_message = e.output.decode()
        print("Error:", error_message)
        return None, error_message