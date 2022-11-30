import json
import os

from web3 import Web3
from solcx import compile_standard, install_solc

from dotenv import load_dotenv
load_dotenv()


with open("./simplestorage.sol", "r") as file:
    simple_storage_file = file.read()

"""
Solidity source code
- Must initialise solc version before compiling
"""
install_solc("0.6.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"simplestorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)

# print(compiled_sol)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)


bytecode = compiled_sol["contracts"]["simplestorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]
abi = compiled_sol["contracts"]["simplestorage.sol"]["SimpleStorage"]["abi"]

# connect to ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
# print(w3.eth.accounts)
chain_id = 1337
my_add = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
prv_key = os.getenv("prv_key")

# create contract
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# build, sign + send transaction
## get latest transaction
nonce = w3.eth.getTransactionCount(my_add)
# print(nonce)

## build transaction
trans = SimpleStorage.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id, 
        "from": my_add, 
        "nonce": nonce
    }
)
# print(trans)

signed_txn = w3.eth.account.sign_transaction(trans, private_key=prv_key)

## send transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)


simple_storage = w3.eth.contract(
    address=tx_receipt.contractAddress, 
    abi=abi
)
print(simple_storage.functions.retrieve().call())
# print(simple_storage.functions.store(15).call())

store_trans = simple_storage.functions.store(15).buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id, 
        "from": my_add,
        "nonce": nonce + 1
    }
)
signed_store_tnx = w3.eth.account.sign_transaction(
    store_trans, 
    private_key=prv_key
)
send_store_tx = w3.eth.send_raw_transaction(signed_store_tnx.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)

print(simple_storage.functions.retrieve().call())