# BTC Backend

This backend must interact with our private Bitcoin Core Full Node.

You will have access to a development server which will have installed the BTC Full Node and you will have to develop the backend project on this server.

Node.js es recomended for the backend but you are free to use other programing language.

All endpoints must accept an additional parameter called "network" where we can specify which network to use: testnet or mainnet. This parameter must be optional, is it is not passed, "mainnet" must be the default value.

For your tests, you will have to make transactions on the testnet so no real money is needed. 

You will have to create a manual of how to install the backend on a production server like DigitalOcean.



## Create multiple addresses

Create an address or multiple addresses of Bitcoin core (BTC) and return the public key of each address created. The private key or any other information about the created addresses must be saved in the backend database in the most secured way, encrypted or using a secured database engine to prevent the wallet addresses to be stolen from hackers.

We will create 14 BTC addresses for each user that signs up to our website. Consider that we will have about 2000 registrations per day. So we will need a custom application that runs on a VPS that creates the BTC wallet addresses. Not using Blockchain API or Coinbase SDK.

These addresses must be valid to receive and send BTC in the blockchain.

### Request

POST `wallets/addresses/`

```json
{
    "number_of_addresses_to_create": 3
}
```

### Response

```json
{
    "addresses": [
        "4a55f6a6d6f5a5a6df6d6a6d6fa6a76aadbbb1",
        "f6d6a6d6fa6a76aadbbb14a55f6a6d6f5a5a6d",
        "dbbb14a55f6a6d6f5a5a6df6d6a6d6fa6a76aa"
    ]
}
```

The response may include any additional information of each generated address. We will store these addresses on our database.



## Get address balance in BTC

Get the balance, in BTC, of the specified BTC address in the URL.

This address must be one of the created addresses on the previous endpoint.

### Request

GET `wallets/addresses/4a55f6a6d6f5a5a6df6d6a6d6fa6a76aadbbb1/balance/`

### Response

```json
{
    "address": "4a55f6a6d6f5a5a6df6d6a6d6fa6a76aadbbb1",
    "balance": 0.00010001
}
```



## Get BTC transfer fee

This endpoint must return the recomended fee to be used when a user wants to send to another address (internal or external).

This fee must be estimated and you must use the algorithms you consider are the best options.

GET `wallets/fee/`

### Response

```json
{
    "fee": 0.00005635
}
```



## Send BTC to an address

Send bitcoins to a local address (created by this backend) or to a external address like Coinbase, Blockchain.info or another one. This transfer must use the blockchain, even if the transfer is between local addresses. So fee must be used as an additional parameter on the endpoint.

### Request

POST `wallets/send/`

```json
{
    "from": "4a55f6a6d6f5a5a6df6d6a6d6fa6a76aadbbb1",
    "to": "dbbb14a55f6a6d6f5a5a6df6d6a6d6fa6a76aa",
    "fee": 0.00001,
    "amount": 0.00187614
}
```

### Input validation

- All fields are required.
- Validate that `from` address has enough balance to send that `amount`.

### Response

```json
{
    "from": "4a55f6a6d6f5a5a6df6d6a6d6fa6a76aadbbb1",
    "to": "dbbb14a55f6a6d6f5a5a6df6d6a6d6fa6a76aa",
    "transation_id": "cb63cb74-61f0-4756-a233-32ce7f3b3569"
}
```

`transation_id` is the ID of the "Send operation" so it can used later to see the status of the operation (for example, the number of confirmations in the blockchain).



## Retrieve transaction information

This endpoint returns the information of a "Send operation", for example, we can see if it is fully confirmed.

### Request

GET `wallets/transaction/cb63cb74-61f0-4756-a233-32ce7f3b3569/`

The `transation_id` is provided in the URL.

### Response

```json
{
    "id": "cb63cb74-61f0-4756-a233-32ce7f3b3570",
    "date": "2020-02-01T16:56:12Z",
    "type": "S",
    "amount": -0.001,
    "fee": -0.001,
    "affected_address": "dbbb14a55f6a6d6f5a5a6df6d6a6d6fa6a76aa",
    "transaction_confirmed": true,
    "confirmations_count": 3,
    ...
    ...
    ...
}
```

Additional information of the transaction must be added in the response if you consider so.



## Get address history

List all operations that affected to the specified address (address created by this backend). The list must ordered by date descendant. Must include the amount (positive or negative) and the balance updated until the row date.

### Request

GET `wallets/address/4a55f6a6d6f5a5a6df6d6a6d6fa6a76aadbbb1/history/`

The `address` is provided in the URL.

### Response

```json
[
    {
        "id": "cb63cb74-61f0-4756-a233-32ce7f3b3569",
        "date": "2020-01-31T16:56:12Z",
        "type": "R",
        "amount": 0.003,
        "fee": 0,
        "affected_address": "dbbb14a55f6a6d6f5a5a6df6d6a6d6fa6a76aa",
        "transaction_confirmed": true,
        "balance": 0.003
    },
    {
        "id": "cb63cb74-61f0-4756-a233-32ce7f3b3570",
        "date": "2020-02-01T16:56:12Z",
        "type": "S",
        "amount": -0.001,
        "fee": -0.001,
        "affected_address": "dbbb14a55f6a6d6f5a5a6df6d6a6d6fa6a76aa",
        "transaction_confirmed": true,
        "balance": 0.001
    },
    {
        "id": "cb63cb74-61f0-4756-a233-32ce7f3b3571",
        "date": "2020-01-31T16:56:12Z",
        "type": "R",
        "amount": 0.001,
        "fee": 0,
        "affected_address": "dbbb14a55f6a6d6f5a5a6df6d6a6d6fa6a76aa",
        "transaction_confirmed": true,
        "balance": 0.002
    }
]
```

`type` must be "S" (Send) or "R" (Receive).
`fee` must show the fee used on the send transaction. If it is possible to know the fee used on an incomming transaction, please show it as "R" type transations as a positive amount. This amount must not be added to the balance.
`affected_address` refers to the destination address if it is type "S" or sender address if it is type "R".
`transaction_confirmed` refers if the transaction is fully confirmed.
`balance` refers to the cummulative balance that is updated after each transaction

Please let me know if any other attribute would be recomended to add on the response schema.




## Webhook: When a local Address Receives an incomming transation (fully confirmed)

This is not an endpoint. It is a webhook.

We would like to detect when any local address receives an incomming transacction (type "R") and it is fully confirmed. When these 2 conditions are met, the backend must call an external endpoint (from our existing website) so we can take an action.

The method of the external endpoint will be `POST` and the URL must be configurable in the settings file of the backend.