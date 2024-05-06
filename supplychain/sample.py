from web3 import Web3

def test_web3_toWei():
    # Replace with your own provider URL or use Infura/Alchemy as appropriate
    web3 = Web3(Web3.HTTPProvider('https://eth-sepolia.g.alchemy.com/v2/NMyx4V3vwR1CGINsvgP-X1JtDNJIQmX6'))
    if not web3.is_connected():
        print("Failed to connect to Ethereum network.")
    else:
        print("Connected successfully.")
        # Test toWei conversion
        result = web3.to_wei(1, 'ether')
        print(f"1 Ether is {result} Wei")

test_web3_toWei()
