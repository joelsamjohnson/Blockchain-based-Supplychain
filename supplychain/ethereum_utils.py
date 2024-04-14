from web3 import Web3
from web3.gas_strategies.rpc import rpc_gas_price_strategy
import json
import os

def get_web3_connection():
    web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545')) # Connect to Ethereum node
    if not web3.is_connected():
            raise Exception("Failed to connect to Ethereum network.")
    return web3

def load_contract_abi(abi_filename):
    abi_path = os.path.join(os.path.dirname(__file__), abi_filename)
    with open(abi_path) as abi_file:
        return json.load(abi_file)

def get_contract_instance(web3, contract_address, abi_filename):
    contract_abi = load_contract_abi(abi_filename)
    return web3.eth.contract(address=contract_address, abi=contract_abi)

def send_transaction(web3, contract, function_name, args, sender_address, sender_private_key):
    web3.eth.set_gas_price_strategy(rpc_gas_price_strategy)
    estimated_gas_price = web3.eth.generate_gas_price()
    if not estimated_gas_price:
        raise Exception("Failed to fetch gas price")

    # Calculate gas limit based on the desired cost (0.01 ETH) and estimated gas price
    desired_cost_eth = 0.01
    desired_cost_wei = web3.toWei(desired_cost_eth, 'ether')
    estimated_gas_limit = contract.get_function_by_name(function_name)(*args).estimateGas({'from': sender_address})
    
    # Adjust gas limit if necessary or leave some buffer
    gas_limit = estimated_gas_limit  # Add any buffer if necessary

    # Calculate maximum affordable gas price within the desired cost
    affordable_gas_price = desired_cost_wei // gas_limit

    # Use the minimum of the estimated gas price and affordable gas price
    gas_price = min(estimated_gas_price, affordable_gas_price)
    function = contract.get_function_by_name(function_name)(*args)
    transaction = function.buildTransaction({
        'from': sender_address,
        'nonce': contract.eth.getTransactionCount(sender_address),
        'gas': gas_limit,
        'gasPrice': gas_price
    })
    signed_txn = contract.eth.account.sign_transaction(transaction, sender_private_key)
    txn_hash = contract.eth.sendRawTransaction(signed_txn.rawTransaction)
    return contract.toHex(txn_hash)




