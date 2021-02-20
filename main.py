from typing import Optional, Set
from fastapi import Body, FastAPI, Query
from pydantic import BaseModel
from datetime import datetime, timedelta

import requests
import time 

app = FastAPI()

#################### Bitcoin Core Configuration ###################
rpc_url = "http://185.21.217.79:18332"
rpc_username = '###'
rpc_password = '###'
###################################################################

#################### Create multiple addresses ####################
###### Request
# POST `wallets/addresses/`
# {
#    "number_of_addresses_to_create": 3
# }
###### Response
# {
#    "addresses": [
#        "4a55f6a6d6f5a5a6df6d6a6d6fa6a76aadbbb1",
#        "f6d6a6d6fa6a76aadbbb14a55f6a6d6f5a5a6d",
#        "dbbb14a55f6a6d6f5a5a6df6d6a6d6fa6a76aa"
#    ]
# }
##################################################################

class addressCount(BaseModel):
	number_of_addresses_to_create:  int

@app.post("/wallets/addresses/")
async def create_addresses(item: addressCount):
	
	try:
		new_addresses = []

		for x in range(item.number_of_addresses_to_create):
			result = await getData("getnewaddress", ["","legacy"])

			if(result != None):
				new_addresses.append(result)

		return { "addresses": new_addresses }
	except:
		return {"error": "connection"}


#################### Get Wallet Balance in BTC ###################
###### Request
# GET `wallets/balance/`
###### Response
# {
#    "balance": 0.00010001
# }
##################################################################

@app.get("/wallets/balance/")
async def get_wallet_balance():
	try:
		result = await getData("getbalance", [])
		return { "balance" : result}
	except:
		return {"error" : "connection"}


################# Get Received Amount of Address #################
###### Request
# GET `wallets/addresses/4a55f6a6d6f5a5a6df6d6a6d6fa6a76aadbbb1/balance/`
###### Response
# {
#    "address": "4a55f6a6d6f5a5a6df6d6a6d6fa6a76aadbbb1",
#    "balance": 0.00010001
# }
##################################################################

@app.get("/wallets/addresses/{request_address}/balance")
async def get_address_balance(request_address: str):
	try:
		result = await getData("getreceivedbyaddress", [request_address, 3])

		return { 
			"address": request_address,
			"balance" : result
		}
	except:
		return {"error" : "connection"}


####################### Get BTC Transfer Fee #####################
###### Request
# GET `wallets/fee/6`
###### Response
# {
#     "fee": 0.00005635
# }
##################################################################

@app.get("/wallets/fee/{block_count}")
async def get_transfer_fee(block_count: int):
	try:
		result = await getData("estimatesmartfee", [block_count])
		if(result == None):
			return {"error" : "EstimateFee"}

        #inp_count = count($network->callCoin('listunspent',[]));
        #trans_size = 180*$inp_count + 64 + $inp_count;

		tx_size = 1024; 
		result = result["feerate"] * tx_size / 1024;

		return {"fee" : result}
	except:
		return {"error" : "connection"}

###################### Send BTC to an address ####################
###### Request
# POST `wallets/send/`
# {
#     "to": "dbbb14a55f6a6d6f5a5a6df6d6a6d6fa6a76aa",
#     "fee": 0.00001,
#     "amount": 0.00187614
# }
###### Response
# {
#     "to": "dbbb14a55f6a6d6f5a5a6df6d6a6d6fa6a76aa",
#     "transation_id": "cb63cb74-61f0-4756-a233-32ce7f3b3569"
# }
##################################################################

class sendBTC(BaseModel):
	to:         str
	fee:        float
	amount:     float

@app.post("/wallets/send/")
async def send_btc(send_info: sendBTC):
	try:
		to_addr = send_info.to
		amount = send_info.amount
		fee = send_info.fee

		result = await getData("getbalance", [])
		if(amount > result):
			return {"error" : "BalanceLow"}

		result = await getData("settxfee", [fee])
		if(result == None):
			return {"error" : "FailSendBTCtoAddress"}

		result = await getData("sendtoaddress", [to_addr, amount, '', '', True])
		if(result == None):
			return {"error" : "FailSendBTCtoAddress"}
		
		return {
			"to": to_addr,
			"transation_id": result
		 }
	except:
		print("=====connection error=====")
		return {"error" : "connection"}

################ Retrieve transaction information ################
###### Request
# GET `wallets/transaction/cb63cb74-61f0-4756-a233-32ce7f3b3569/`
###### Response
# {
#     "id": "cb63cb74-61f0-4756-a233-32ce7f3b3570",
#     "date": "2020-02-01T16:56:12Z",
#     "type": "S",
#     "amount": -0.001,
#     "fee": -0.001,
#     "affected_address": "dbbb14a55f6a6d6f5a5a6df6d6a6d6fa6a76aa",
#     "transaction_confirmed": true,
#     "confirmations_count": 3,
# }
##################################################################

@app.get("/wallets/transaction/{transaction_id}")
async def retrieve_transaction_info(transaction_id: str):
	try:
		result = await getData("gettransaction", [transaction_id])
		if(result == None):
			return {"error" : "RetrieveTransaction"}
		
		address_list = []
		for x in range(len(result["details"])):
			tx_details = result["details"][x]
			address_list.append(
				{
					"address":	tx_details["address"],
					"amount":	tx_details["amount"],
					"fee":		"" if "fee" not in tx_details else tx_details["fee"]
				}
			)

		return {
					"id":                       result["txid"],
					"date":                     datetime.fromtimestamp(result["time"]),
					"transaction_type":         "S" if "fee" in result else "R",
					"amount":                   result["amount"],
					"fee":                      "" if "fee" not in result else result["fee"],
					"transaction_confirmed":    True if result["confirmations"] >=3 else False,
					"confirmations_count":      result["confirmations"],
					"affected_address":         address_list
				}
	except:
		return {"error" : "connection"}

###################### Get Transaction History ######################
###### Request
# GET `wallets/history/`
###### Response
# [
#     {
#         "id": "cb63cb74-61f0-4756-a233-32ce7f3b3569",
#         "date": "2020-01-31T16:56:12Z",
#         "type": "R",
#         "amount": 0.003,
#         "fee": 0,
#         "affected_address": "dbbb14a55f6a6d6f5a5a6df6d6a6d6fa6a76aa",
#         "transaction_confirmed": true,
#     },
#     {
#         "id": "cb63cb74-61f0-4756-a233-32ce7f3b3570",
#         "date": "2020-02-01T16:56:12Z",
#         "type": "S",
#         "amount": -0.001,
#         "fee": -0.001,
#         "affected_address": "dbbb14a55f6a6d6f5a5a6df6d6a6d6fa6a76aa",
#         "transaction_confirmed": true,
#     },
#     {
#         "id": "cb63cb74-61f0-4756-a233-32ce7f3b3571",
#         "date": "2020-01-31T16:56:12Z",
#         "type": "R",
#         "amount": 0.001,
#         "fee": 0,
#         "affected_address": "dbbb14a55f6a6d6f5a5a6df6d6a6d6fa6a76aa",
#         "transaction_confirmed": true,
#     }
##################################################################

@app.get("/wallets/history/")
async def get_transaction_history(request_address: str):
	try:
		transaction_history = []

		result = await getData("listtransactions", [])
		if(result == None):
			return {"error" : "Transactoin History"}
		
		for x in range(len(result)):
			addr_info = result[x]

			transaction_history.append(
				{
					"id":                       addr_info["txid"],
					"date":                     datetime.fromtimestamp(addr_info["time"]),
					"type":                     "S" if addr_info["category"] == "send" else "R",
					"amount":                   addr_info["amount"],
					"fee":                      "" if "fee" not in addr_info else addr_info["fee"],
					"affected_address":         addr_info["address"],
					"transaction_confirmed":    True if addr_info["confirmations"] >=3 else False,
				}
			)
		return transaction_history
	except:
		return {"error" : "connection"}

###################### Get Address History ######################
###### Request
# GET `wallets/list_input_transactions/4a55f6a6d6f5a5a6df6d6a6d6fa6a76aadbbb1/`
###### Response
# [
#     {
#         "id": "cb63cb74-61f0-4756-a233-32ce7f3b3569",
#         "date": "2020-01-31T16:56:12Z",
#         "amount": 0.003,
#         "fee": 0,
#         "affected_address": "dbbb14a55f6a6d6f5a5a6df6d6a6d6fa6a76aa",
#         "transaction_confirmed": true,
#     },
#     {
#         "id": "cb63cb74-61f0-4756-a233-32ce7f3b3571",
#         "date": "2020-01-31T16:56:12Z",
#         "amount": 0.001,
#         "fee": 0,
#         "affected_address": "dbbb14a55f6a6d6f5a5a6df6d6a6d6fa6a76aa",
#         "transaction_confirmed": true,
#     }
##################################################################

@app.get("/wallets/list_input_transactions/{request_address}/")
async def list_input_transactions(request_address: str):
	try:
		address_history = []

		result = await getData("listreceivedbyaddress", [3, False, True, request_address])
		if(result == None):
			return {"error" : "Address History"}
		
		if(len(result)<=0):
			return {"error" : "invalid address(no transaction)"}

		txids = result[0]["txids"]
		for x in range(len(txids)):
			txid = txids[x]

			tx_info = await getData("gettransaction", [txid])
			if(tx_info == None):
				return {"error" : "RetrieveTransactionInAddressHistory"}
			
			address_history.append(
				{
					"id":                       tx_info["txid"],
					"date":                     datetime.fromtimestamp(tx_info["time"]),
					"type":                     "R",
					"amount":                   tx_info["amount"],
					"affected_address":         tx_info["details"][0]["address"],
					"transaction_confirmed":    True if tx_info["confirmations"] >= 3 else False,
					"balance":                  ""  
				}
			)
		return address_history
	except:
		return {"error" : "connection"}

###################### Get New Deposited History ######################
###### Request
# GET `wallets/new_deposit_list/`
###### Response
# [
#     {
#         "address": "cb63cb74-61f0-4756-a233-32ce7f3b3569",
#         "amount": 0.003,
#         "date": "2020-01-31T16:56:12Z",
#     }
# ]
##################################################################

@app.get("/wallets/deposit/")
async def get_new_deposit_list(request_address: str):
	try:
		transaction_history = []

		result = await getData("listtransactions", [])
		if(result == None):
		 	return {"error" : "New Deposited History"}

		for x in range(len(result)):
			addr_info = result[x]

			if(addr_info["category"] == "send"):
				continue
			if(addr_info["confirmations"] < 3):
				continue
			if(time.time() - addr_info["time"] > 108000 ):
				break

			transaction_history.append(
				{
					"address": addr_info["address"],
					"amount":  addr_info["amount"],
					"date":    datetime.fromtimestamp(addr_info["time"]),
				}
			)
		return transaction_history
	except:
		return {"error" : "connection"}


async def getData(method, params):
	headerObj = {"Content-type" : "application/json"}

	jsonObj = { 
		"method" : method,
		"params" : params
	}

	try:
		result = requests.post(rpc_url, json = jsonObj, auth = (rpc_username, rpc_password), headers = headerObj) 
		addrJson = result.json()

		if(addrJson["error"] != None):
		   return None

		return addrJson["result"]
	except:
		return {"error":"connection"}