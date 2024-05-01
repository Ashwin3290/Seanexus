#!/bin/bash

# Ensure environment variables are set correctly
export CORE_PEER_TLS_ENABLED=true
export ORDERER_CA="${PWD}/artifacts/channel/crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem"
export PEER0_ORG1_CA="${PWD}/artifacts/channel/crypto-config/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt"
export PEER0_ORG2_CA="${PWD}/artifacts/channel/crypto-config/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt"
export FABRIC_CFG_PATH="${PWD}/artifacts/channel/config/"
export PRIVATE_DATA_CONFIG="${PWD}/artifacts/private-data/collections_config.json"
export CHANNEL_NAME="mychannel"

# Define function to set globals for Peer0Org1
setGlobalsForPeer0Org1() {
    export CORE_PEER_LOCALMSPID="Org1MSP"
    export CORE_PEER_TLS_ROOTCERT_FILE="$PEER0_ORG1_CA"
    export CORE_PEER_MSPCONFIGPATH="${PWD}/artifacts/channel/crypto-config/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp"
    export CORE_PEER_ADDRESS=localhost:7051
}

# # Define function to invoke chaincode
chaincodeInvoke() {
    setGlobalsForPeer0Org1

    ## Construct JSON payload
    payload='{"function": "'"$1"'", "Args":['
    shift
    while [ "$#" -gt 1 ]; do
        payload+="\"$1\", "
        shift
    done
    payload+="\"$1\"]}"

    ## Push transaction data
    peer chaincode invoke -o localhost:7050 \
        --ordererTLSHostnameOverride orderer.example.com \
        --tls "$CORE_PEER_TLS_ENABLED" \
        --cafile "$ORDERER_CA" \
        -C "mychannel" -n "transaction" \
        --peerAddresses localhost:7051 --tlsRootCertFiles "$PEER0_ORG1_CA" \
        --peerAddresses localhost:9051 --tlsRootCertFiles "$PEER0_ORG2_CA" \
        -c "$payload"
}

chaincodeInvoke "$@"
