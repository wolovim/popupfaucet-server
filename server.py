from flask import Flask, request, jsonify

from web3 import Web3, EthereumTesterProvider
import os
import time
import json

app = Flask(__name__)

# Initialize Web3
# rpc_url = '...'
# w3 = Web3(Web3.HTTPProvider(rpc_url))
w3 = Web3(EthereumTesterProvider())

# Check connection
if not w3.is_connected():
    raise ConnectionError("Failed to connect to the Ethereum network")

# Contract details
# contract_address = 'YOUR_CONTRACT_ADDRESS'  # Replace with your contract address
# contract_abi = 'YOUR_CONTRACT_ABI'  # Replace with your contract ABI

# wallet_address = w3.eth.accounts[0]  # eth-tester
# private_key = os.getenv('PRIVATE_KEY')  # Load private key from environment variable

# Initialize contract
# contract = w3.eth.contract(address=contract_address, abi=contract_abi)

with open("artifacts.json") as f:
    artifacts = json.load(f)

contract_factory = w3.eth.contract(
    abi=artifacts["abi"], bytecode=artifacts["deploymentBytecode"]["bytecode"]
)
tx_hash = contract_factory.constructor(w3.eth.accounts[0]).transact(
    {"from": w3.eth.accounts[0]}
)
contract = w3.eth.contract(
    address=w3.eth.get_transaction_receipt(tx_hash)["contractAddress"],
    abi=artifacts["abi"],
)


@app.route("/availability", methods=["GET"])
def check_availability():
    event_code = request.args.get("event_code")
    if not event_code:
        return jsonify({"error": "event_code parameter is required"}), 400

    # encoded_event_code = w3.solidityKeccak(['string'], [event_code]).hex()
    try:
        # available = contract.functions.yourMappingFunction(encoded_event_code).call()
        # Mock value
        is_available = True
        return jsonify({"event_code": event_code, "is_available": is_available}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/status", methods=["GET"])
def check_status():
    event_code = request.args.get("event_code")
    if not event_code:
        return jsonify({"error": "event_code parameter is required"}), 400

    # encoded_event_code = w3.solidityKeccak(['string'], [event_code]).hex()
    try:
        # available_ether = contract.functions.yourMappingFunction(encoded_event_code).call()
        # ether_in_wei = w3.fromWei(available_ether, 'ether')
        # Mock value
        ether_in_wei = 1.5
        return jsonify({"event_code": event_code, "available_ether": ether_in_wei}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/seeder-funded", methods=["POST"])
def check_seeder_funded():
    data = request.json
    pk = data.get("pk")
    acct = w3.eth.account.from_key(pk)

    # mock transfer
    w3.eth.send_transaction(
        {
            "from": w3.eth.accounts[1],
            "to": acct.address,
            "value": w3.to_wei("1", "ether"),
        }
    )

    # Convert ether amount to Wei
    wei_amount = w3.eth.get_balance(acct.address)
    print(f"wei_amount: {wei_amount}")

    if wei_amount == 0:
        return jsonify({"error": "Insufficient balance"}), 400
    else:
        return jsonify({"balance": wei_amount}), 200


@app.route("/create-faucet", methods=["POST"])
def create_faucet():
    data = request.json
    event_code = data.get("event_code")
    pk = data.get("pk")
    acct = w3.eth.account.from_key(pk)

    if not event_code:
        return jsonify({"error": "Event code is required"}), 400

    try:
        # Encode event code
        # encoded_event_code = w3.solidity_keccak(["string"], [event_code]).hex()
        # print(f"encoded_event_code: {encoded_event_code}")

        # Build transaction
        gas_limit = contract.functions.seedFunds(event_code).estimate_gas(
            {"from": acct.address, "value": 1}
        )
        gas_price = w3.to_wei("5", "gwei")
        gas_cost = gas_limit * gas_price
        value = w3.eth.get_balance(acct.address) - gas_cost
        txn = contract.functions.seedFunds(event_code).build_transaction(
            {
                "gas": gas_limit,
                "gasPrice": gas_price,
                "nonce": 0,
                "value": value,
            }
        )

        # Sign transaction
        signed_txn = w3.eth.account.sign_transaction(txn, private_key=pk)

        # Send transaction
        txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        return jsonify({"txn_hash": txn_hash.hex()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/top-up-faucet", methods=["POST"])
def top_up_faucet():
    data = request.json
    event_code = data.get("event_code")
    ether_amount = data.get("ether_amount")

    if not event_code or not ether_amount:
        return jsonify({"error": "Event code and ether amount are required"}), 400

    try:
        # Encode event code
        # encoded_event_code = w3.solidityKeccak(['string'], [event_code]).hex()

        # Convert ether amount to Wei
        # wei_amount = w3.toWei(ether_amount, 'ether')

        # Build transaction
        # txn = contract.functions.topUpFaucet(encoded_event_code).buildTransaction({
        #     'chainId': 1,  # Mainnet
        #     'gas': 2000000,
        #     'gasPrice': w3.toWei('50', 'gwei'),
        #     'nonce': w3.eth.getTransactionCount(wallet_address),
        #     'value': wei_amount,
        # })

        # Sign transaction
        # signed_txn = w3.eth.account.signTransaction(txn, private_key=private_key)

        # Send transaction
        # txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

        # Mock transaction hash
        txn_hash = "0xabcdef1234567890"
        return jsonify({"txn_hash": txn_hash}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/claim-faucet", methods=["POST"])
def claim_faucet():
    data = request.json
    event_code = data.get("event_code")
    address = data.get("address")

    if not event_code:
        return jsonify({"error": "Event code is required"}), 400
    if not address:
        return jsonify({"error": "Address is required"}), 400

    try:
        # Encode event code
        # encoded_event_code = w3.solidityKeccak(['string'], [event_code]).hex()

        # Build transaction
        # txn = contract.functions.claimFaucet(encoded_event_code).buildTransaction({
        #     'chainId': 1,  # Mainnet
        #     'gas': 2000000,
        #     'gasPrice': w3.toWei('50', 'gwei'),
        #     'nonce': w3.eth.getTransactionCount(wallet_address),
        # })

        # Sign transaction
        # signed_txn = w3.eth.account.signTransaction(txn, private_key=private_key)

        # Send transaction
        # txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

        # Mock transaction hash
        txn_hash = "0xfeedfacecafebeef"
        return jsonify({"txn_hash": txn_hash}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
