
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"strconv"
	"time"

	"github.com/hyperledger/fabric-chaincode-go/shim"
	sc "github.com/hyperledger/fabric-protos-go/peer"
	// "github.com/hyperledger/fabric/common/flogging"

	// "github.com/hyperledger/fabric-chaincode-go/pkg/cid"
)

// SmartContract represents the chaincode for the fishing network
type SmartContract struct {
}

// FishingLot represents the data structure for a fishing lot
type FishingLot struct {
	TransactionID string `json:"transactionID"`
	VendorID    string `json:"vendorID"`
	CatchWeight int    `json:"catchWeight"`
	Location    string `json:"location"`
	DateTime    string `json:"dateTime"`
}

// Init ;  Method for initializing smart contract
func (s *SmartContract) Init(APIstub shim.ChaincodeStubInterface) sc.Response {
	return shim.Success(nil)
}

func (s *SmartContract) PushData(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {
	if len(args) != 5 {
		return shim.Error("Incorrect number of arguments. Expecting 4")
	}

	vendorID := args[1]
	catchWeight, err := strconv.Atoi(args[2])
	if err != nil {
		return shim.Error("Invalid catch weight: " + err.Error())
	}
	location := args[3]
	dateTime := args[4]

	transactionID := args[0]

	fishingLot := FishingLot{
		TransactionID: transactionID,
		VendorID:      vendorID,
		CatchWeight:   catchWeight,
		Location:      location,
		DateTime:      dateTime,
	}
	fishingLotAsBytes, _ := json.Marshal(fishingLot)
	err = APIstub.PutState(transactionID, fishingLotAsBytes)
	if err != nil {
		return shim.Error("Failed to store fishing lot data: " + err.Error())
	}

	return shim.Success(fishingLotAsBytes)
}


// QueryData function to retrieve fishing lot data from the ledger
func (s *SmartContract) QueryData(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {
	if len(args) != 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}

	transactionID := args[0]

	fishingLotAsBytes, err := APIstub.GetState(transactionID)
	if err != nil {
		return shim.Error("Failed to retrieve fishing lot data: " + err.Error())
	} else if fishingLotAsBytes == nil {
		return shim.Error("Fishing lot does not exist")
	}

	return shim.Success(fishingLotAsBytes)
}

// QueryDataByTxID function to retrieve fishing lot data history by transaction ID
func (s *SmartContract) QueryDataByTxID(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {
	if len(args) != 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}

	txID := args[0]

	resultsIterator, err := APIstub.GetHistoryForKey(txID)
	if err != nil {
		return shim.Error("Failed to retrieve fishing lot data history: " + err.Error())
	}
	defer resultsIterator.Close()

	var buffer bytes.Buffer
	buffer.WriteString("[")

	bArrayMemberAlreadyWritten := false
	for resultsIterator.HasNext() {
		response, err := resultsIterator.Next()
		if err != nil {
			return shim.Error("Failed to retrieve fishing lot data history: " + err.Error())
		}

		if bArrayMemberAlreadyWritten {
			buffer.WriteString(",")
		}

		buffer.WriteString("{\"TxId\":")
		buffer.WriteString("\"")
		buffer.WriteString(response.TxId)
		buffer.WriteString("\"")

		buffer.WriteString(", \"Value\":")
		if response.IsDelete {
			buffer.WriteString("null")
		} else {
			buffer.WriteString(string(response.Value))
		}

		buffer.WriteString(", \"Timestamp\":")
		buffer.WriteString("\"")
		buffer.WriteString(time.Unix(response.Timestamp.Seconds, int64(response.Timestamp.Nanos)).String())
		buffer.WriteString("\"")

		buffer.WriteString(", \"IsDelete\":")
		buffer.WriteString("\"")
		buffer.WriteString(strconv.FormatBool(response.IsDelete))
		buffer.WriteString("\"")

		buffer.WriteString("}")

		bArrayMemberAlreadyWritten = true
	}

	buffer.WriteString("]")

	return shim.Success(buffer.Bytes())
}

// QueryDataByVendorID function to retrieve fishing lot data by vendor ID
func (s *SmartContract) QueryDataByVendorID(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {
	if len(args) != 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}

	vendorID := args[0]

	queryString := fmt.Sprintf("{\"selector\":{\"vendorID\":\"%s\"}}", vendorID)
	resultsIterator, err := APIstub.GetQueryResult(queryString)
	if err != nil {
		return shim.Error("Failed to retrieve fishing lot data: " + err.Error())
	}
	defer resultsIterator.Close()

	var buffer bytes.Buffer
	buffer.WriteString("[")

	bArrayMemberAlreadyWritten := false
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return shim.Error("Failed to retrieve fishing lot data: " + err.Error())
		}

		if bArrayMemberAlreadyWritten {
			buffer.WriteString(",")
		}

		buffer.WriteString(string(queryResponse.Value))

		bArrayMemberAlreadyWritten = true
	}

	buffer.WriteString("]")

	return shim.Success(buffer.Bytes())
}

// QueryDataByLocation function to retrieve fishing lot data by location
func (s *SmartContract) QueryDataByLocation(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {
	if len(args) != 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}

	location := args[0]

	resultsIterator, err := APIstub.GetStateByRange(location+"0", location+"z")
	if err != nil {
		return shim.Error("Failed to retrieve fishing lot data: " + err.Error())
	}
	defer resultsIterator.Close()

	var buffer bytes.Buffer
	buffer.WriteString("[")

	bArrayMemberAlreadyWritten := false
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return shim.Error("Failed to retrieve fishing lot data: " + err.Error())
		}

		if bArrayMemberAlreadyWritten {
			buffer.WriteString(",")
		}

		buffer.WriteString(string(queryResponse.Value))

		bArrayMemberAlreadyWritten = true
	}

	buffer.WriteString("]")

	return shim.Success(buffer.Bytes())
}

// Invoke function to handle chaincode invocations
func (s *SmartContract) Invoke(APIstub shim.ChaincodeStubInterface) sc.Response {
	function, args := APIstub.GetFunctionAndParameters()

	switch function {
	case "pushData":
		return s.PushData(APIstub, args)
	case "queryData":
		return s.QueryData(APIstub, args)
	case "queryDataByTxID":
		return s.QueryDataByTxID(APIstub, args)
	case "queryDataByVendorID":
		return s.QueryDataByVendorID(APIstub, args)
	case "queryDataByLocation":
		return s.QueryDataByLocation(APIstub, args)
	default:
		return shim.Error("Invalid function name. Expecting 'pushData', 'queryData', 'queryDataByTxID', 'queryDataByVendorID', or 'queryDataByLocation'")
	}
}

func main() {
	err := shim.Start(new(SmartContract))
	if err != nil {
		fmt.Printf("Error creating new Smart Contract: %s", err)
	}
}
