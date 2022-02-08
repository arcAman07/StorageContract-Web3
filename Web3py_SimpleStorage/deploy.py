from solcx import compile_standard, compile_files, link_code, install_solc
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()
import os

install_solc("0.6.0")
with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", ",metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# for connecting to ganache
w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
chaind_id = 1337
my_address = "0xD3954aC75a7B0D9C093E6D9dC32f706e06cD84c5"
private_key = os.getenv("PRIVATE_KEY")
# Create the contract in python
contract = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.getTransactionCount(my_address)
print(nonce)
# 1) Build the transaction
transaction = contract.constructor().buildTransaction(
    {
        "chainId": chaind_id,
        "from": my_address,
        "nonce": nonce,
        "gas": 1728712,
        "gasPrice": w3.toWei("21", "gwei"),
    }
)

# 2) Sign the transaction
signed_txn = w3.eth.account.signTransaction(transaction, private_key=private_key)
# 3) Send the transaction
print("Deploying the contract...")
txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.waitForTransactionReceipt(txn_hash)
print("Deployed")
# Working with the contract
# Contract address
# Contract abi
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call
# Transaction
print(simple_storage.functions.retrieve().call())
print("Updating the contract...")
store_transaction = simple_storage.functions.store(12).buildTransaction(
    {
        "chainId": chaind_id,
        "from": my_address,
        "nonce": nonce+1,
        "gas": 1728712,
        "gasPrice": w3.toWei("21", "gwei"),
    })
signed_store_txn = w3.eth.account.signTransaction(store_transaction, private_key=private_key)
print("Contract Updated")

transaction_hash = w3.eth.sendRawTransaction(signed_store_txn.rawTransaction)
store_tx_receipt = w3.eth.waitForTransactionReceipt(transaction_hash)
print(simple_storage.functions.retrieve().call())