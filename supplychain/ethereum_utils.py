from web3 import Web3
import json
import os

def get_web3_connection():
    web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545/')) # Connect to Ethereum node
    if not web3.is_connected():
            raise Exception("Failed to connect to Ethereum network.")
    return web3

def load_contract_abi(abi_filename):
    # Construct the path from the ethereum_utils.py file to the ABI file in the static directory
    abi_path = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'contracts', abi_filename)
    print("Loading ABI from:", abi_path)  # This will show you the constructed path
    try:
        with open(abi_path) as abi_file:
            return json.load(abi_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Unable to find the ABI file at {abi_path}")

def get_contract_instance(web3, contract_address, abi_filename):
    # Ensure address is in checksum format
    checksum_address = Web3.to_checksum_address(contract_address)
    # Load the ABI
    with open(abi_filename, 'r') as file:
        contract_abi = json.load(file)
    # Create the contract instance
    return web3.eth.contract(address=checksum_address, abi=contract_abi)

def send_transaction(web3, contract, function_name, args, sender_address, sender_private_key):
    account_balance = web3.eth.get_balance(sender_address)
    print(f"Account Balance: {web3.from_wei(account_balance, 'ether')} ETH")

    function = contract.get_function_by_name(function_name)(*args)
    transaction = function.build_transaction({
        'from': sender_address,
        'nonce': web3.eth.get_transaction_count(sender_address),
        'gasPrice': web3.eth.gas_price,  # Consider adjusting this based on network conditions
        'gas': function.estimate_gas({'from': sender_address}),  # Dynamically estimate gas
    })

    transaction_cost = transaction['gas'] * transaction['gasPrice']
    print(f"Transaction Cost Estimate: {web3.from_wei(transaction_cost, 'ether')} ETH")

    if transaction_cost > account_balance:
        print("Insufficient funds to cover the transaction cost.")
        return "Error: Insufficient funds."

    # Sign the transaction
    signed_txn = web3.eth.account.sign_transaction(transaction, sender_private_key)

    # Send the transaction
    txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return txn_hash.hex()

# Assuming you have initialized `web3`, `contract`, etc. appropriately
