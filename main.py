import requests
import json
import csv

url = "http://localhost:8545"

headers = {
'Content-Type': 'application/json',
}

def get_transaction_trace(tx_hash):
    return send_rpc_request("debug_traceTransaction", [tx_hash, {"tracer": "callTracer"}])

def get_balance(address):
    result = send_rpc_request("eth_getBalance", [address, "latest"]).get('result')
    balance_wei = int(result, 16)  # Convert hex balance to integer (Wei)
    balance_ether = balance_wei / (10 ** 18)  # Convert Wei to Ether
    return balance_ether

def send_rpc_request(method, params, request_id=1):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": request_id
    }
    response = requests.post(url, json=payload)
    return response.json()

def is_contract(address):
    # eth_getCode returns '0x' for EOAs and contract bytecode for contracts
    code = send_rpc_request("eth_getCode", [address, "latest"]).get('result')
    return code != '0x'

# Loop over block range 100 to 200 to count contract interactions
def count_contract_interactions(start_block, end_block):

    wallets = set()  # Use a set to avoid duplicates

    contract_interactions = {}

    for block_number in range(start_block, end_block + 1):
        block_data = get_block_by_number(block_number)

        if block_data:
            for tx in block_data['transactions']:
                wallets.add(tx['from'])  # Sender wallet
                # Check if the transaction creates a contract (to field is None or 0x0)
                if tx['to'] is None:
                    contract_address = tx['from']  # Contract creator (new contract deployed)
                else:
                    contract_address = tx['to']  # Contract interaction

                # Check if it's a smart contract
                if is_contract(contract_address):
                    
                    if contract_address not in contract_interactions:
                        contract_interactions[contract_address] = 0
                    contract_interactions[contract_address] += 1
                else:
                    wallets.add(tx['to'])

                 #Count transaction trace for internal calls
                #print(get_transaction_trace(tx['hash']).get('result'))
                #print('-----------------------------------')
                internal_calls = get_transaction_trace(tx['hash']).get('result').get('calls')
                if internal_calls:
                    contract_interactions[contract_address] += len(internal_calls)




    return contract_interactions, wallets

# Function to sort contracts by interaction count
def sort_contracts_by_interactions(contract_interactions):
    sorted_contracts = sorted(contract_interactions.items(), key=lambda x: x[1], reverse=True)
    return sorted_contracts

def get_sorted_wallet_balances(wallets):
    wallet_balances = {}

    for wallet in wallets:
        balance = get_balance(wallet)
        wallet_balances[wallet] = balance

    # Sort wallets by balance in descending order
    sorted_wallets = sorted(wallet_balances.items(), key=lambda x: x[1], reverse=True)
    return sorted_wallets

def get_block_by_number(block_number):
    block_hex = hex(block_number)  
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBlockByNumber",
        "params": [block_hex, True],  
        "id": block_number
    }
    response = requests.post(url, json=payload)
    return response.json().get('result')

# Count and sort contract interactions between blocks 100 and 200
contract_interactions, wallets = count_contract_interactions(100, 200)
sorted_contracts = sort_contracts_by_interactions(contract_interactions)
sorted_wallets = get_sorted_wallet_balances(wallets)

# Output the sorted list of contracts
print("Smart Contracts sorted by interactions between blocks 100 and 200:")
for contract, count in sorted_contracts:
    print(f"Contract: {contract}, Interactions: {count}")

print("Wallets sorted by balance between blocks 100 and 200:")
for wallet, balance in sorted_wallets:
    print(f"Wallet: {wallet}, Balance: {balance} ETH")



def save_to_csv(sorted_wallets, filename="wallet_balances.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Wallet Address", "Balance (ETH)"])  # CSV Header
        for wallet, balance in sorted_wallets:
            writer.writerow([wallet, balance])  # Writing wallet and balance

def save_interaction_counts_to_csv(interaction_counts, filename="contract_interactions.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Contract Address", "Interaction Count"])  # CSV Header
        for contract, count in interaction_counts.items():
            writer.writerow([contract, count])  # Writing contract address and count

save_to_csv(sorted_wallets)
save_interaction_counts_to_csv(contract_interactions)
