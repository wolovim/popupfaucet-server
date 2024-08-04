from flask import Flask, request, jsonify

# from web3 import Web3
import os
import time

app = Flask(__name__)

# Initialize Web3
# rpc_url = '...'
# web3 = Web3(Web3.HTTPProvider(rpc_url))

# Check connection
# if not web3.is_connected():
#     raise ConnectionError("Failed to connect to the Ethereum network")

# Contract details
# contract_address = 'YOUR_CONTRACT_ADDRESS'  # Replace with your contract address
# contract_abi = 'YOUR_CONTRACT_ABI'  # Replace with your contract ABI

# Wallet details (keep your private key secure)
wallet_address = "YOUR_WALLET_ADDRESS"  # Replace with your wallet address
# private_key = os.getenv('PRIVATE_KEY')  # Load private key from environment variable

# Initialize contract
# contract = web3.eth.contract(address=contract_address, abi=contract_abi)


@app.route("/status", methods=["GET"])
def check_status():
    event_code = request.args.get("event_code")
    if not event_code:
        return jsonify({"error": "event_code parameter is required"}), 400

    # encoded_event_code = web3.solidityKeccak(['string'], [event_code]).hex()
    try:
        # available_ether = contract.functions.yourMappingFunction(encoded_event_code).call()
        # ether_in_wei = web3.fromWei(available_ether, 'ether')
        # Mock value
        ether_in_wei = 1.5
        return jsonify({"event_code": event_code, "available_ether": ether_in_wei}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/create-faucet", methods=["POST"])
def create_faucet():
    data = request.json
    event_code = data.get("event_code")
    ether_amount = data.get("ether_amount")

    if not event_code or not ether_amount:
        return jsonify({"error": "Event code and ether amount are required"}), 400

    try:
        # Encode event code
        # encoded_event_code = web3.solidityKeccak(['string'], [event_code]).hex()

        # Convert ether amount to Wei
        # wei_amount = web3.toWei(ether_amount, 'ether')

        # Build transaction
        # txn = contract.functions.createFaucet(encoded_event_code).buildTransaction({
        #     'chainId': 1,  # Mainnet
        #     'gas': 2000000,
        #     'gasPrice': web3.toWei('50', 'gwei'),
        #     'nonce': web3.eth.getTransactionCount(wallet_address),
        #     'value': wei_amount,
        # })

        # Sign transaction
        # signed_txn = web3.eth.account.signTransaction(txn, private_key=private_key)

        # Send transaction
        # txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)

        # Mock transaction hash
        txn_hash = "0x1234567890abcdef"
        return jsonify({"txn_hash": txn_hash}), 200
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
        # encoded_event_code = web3.solidityKeccak(['string'], [event_code]).hex()

        # Convert ether amount to Wei
        # wei_amount = web3.toWei(ether_amount, 'ether')

        # Build transaction
        # txn = contract.functions.topUpFaucet(encoded_event_code).buildTransaction({
        #     'chainId': 1,  # Mainnet
        #     'gas': 2000000,
        #     'gasPrice': web3.toWei('50', 'gwei'),
        #     'nonce': web3.eth.getTransactionCount(wallet_address),
        #     'value': wei_amount,
        # })

        # Sign transaction
        # signed_txn = web3.eth.account.signTransaction(txn, private_key=private_key)

        # Send transaction
        # txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)

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
        # encoded_event_code = web3.solidityKeccak(['string'], [event_code]).hex()

        # Build transaction
        # txn = contract.functions.claimFaucet(encoded_event_code).buildTransaction({
        #     'chainId': 1,  # Mainnet
        #     'gas': 2000000,
        #     'gasPrice': web3.toWei('50', 'gwei'),
        #     'nonce': web3.eth.getTransactionCount(wallet_address),
        # })

        # Sign transaction
        # signed_txn = web3.eth.account.signTransaction(txn, private_key=private_key)

        # Send transaction
        # txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)

        # Mock transaction hash
        txn_hash = "0xfeedfacecafebeef"
        return jsonify({"txn_hash": txn_hash}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
