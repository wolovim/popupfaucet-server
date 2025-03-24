import os
import json
from flask import Flask, request, jsonify
from web3 import HTTPProvider, Web3, EthereumTesterProvider
from dotenv import load_dotenv
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
load_dotenv()

DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

# Initialize Web3
w3_tester = Web3(EthereumTesterProvider())
w3_op_sepolia = Web3(HTTPProvider(os.getenv("OP_SEPOLIA_URL")))
w3_base_sepolia = Web3(HTTPProvider(os.getenv("BASE_SEPOLIA_URL")))
w3_sepolia = Web3(HTTPProvider(os.getenv("SEPOLIA_URL")))

# Deployments:
ADMIN_PK = os.getenv("POPUPFAUCET_ADMIN_PK")
DEPLOY_OP_SEPOLIA = os.getenv("OP_SEPOLIA_FAUCET_ADDRESS")
DEPLOY_BASE_SEPOLIA = os.getenv("BASE_SEPOLIA_FAUCET_ADDRESS")
DEPLOY_SEPOLIA = os.getenv("ETH_SEPOLIA_FAUCET_ADDRESS")

with open("artifacts.json") as f:
    artifacts = json.load(f)

w3o = w3_op_sepolia
w3b = w3_base_sepolia
w3s = w3_sepolia

admin_account = w3o.eth.account.from_key(ADMIN_PK)

o_contract = w3o.eth.contract(
    address=DEPLOY_OP_SEPOLIA,
    abi=artifacts["abi"],
)
b_contract = w3b.eth.contract(
    address=DEPLOY_BASE_SEPOLIA,
    abi=artifacts["abi"],
)
s_contract = w3s.eth.contract(
    address=DEPLOY_SEPOLIA,
    abi=artifacts["abi"],
)

networks = {
    "optimism-sepolia": {"w3": w3o, "contract": o_contract},
    "base-sepolia": {"w3": w3b, "contract": b_contract},
    "sepolia": {"w3": w3s, "contract": s_contract},
}
# Check connection
for key in networks.keys():
    if not networks[key]["w3"].is_connected():
        raise ConnectionError(f"Failed to connect to {key} network")


def get_w3_and_contract(network: str):
    return networks[network]["w3"], networks[network]["contract"]


@app.route("/availability", methods=["GET"])
def check_availability():
    name = request.args.get("name")
    network = request.args.get("network")
    _, contract = get_w3_and_contract(network)

    if not name:
        return jsonify({"error": "name parameter is required"}), 400

    try:
        is_available = contract.functions.eventNameAvailable(name).call()
        return jsonify({"name": name, "is_available": is_available}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route("/status", methods=["GET"])
def check_status():
    name = request.args.get("name")
    network = request.args.get("network")
    w3, contract = get_w3_and_contract(network)
    print(w3, contract)
    if not name:
        return jsonify({"error": "name parameter is required"}), 400

    try:
        event_name_unclaimed = contract.functions.eventNameAvailable(name).call()
        print(f"event_name_unclaimed: {event_name_unclaimed}")
        if event_name_unclaimed:
            return jsonify({"event_exists": False, "available_ether": 0}), 200

        funds_available = contract.functions.eventFundsAvailable(name).call()
        print(f"funds_available: {funds_available}")
        ether_in_wei = w3.from_wei(funds_available, "ether")
        return jsonify({"event_exists": True, "available_ether": ether_in_wei}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/seeder-funded", methods=["POST"])
def check_seeder_funded():
    data = request.json
    pk = data.get("pk")
    network = data.get("network")
    w3, _ = get_w3_and_contract(network)
    acct = w3.eth.account.from_key(pk)

    if DEV_MODE:
        # auto-seed with eth-tester
        w3.eth.send_transaction(
            {
                "from": w3.eth.accounts[1],
                "to": acct.address,
                "value": w3.to_wei("1", "ether"),
            }
        )

    # Convert ether amount to Wei
    wei_amount = w3.eth.get_balance(acct.address)
    print(f"network: {network}, address: {acct.address}, wei_amount: {wei_amount}")

    if wei_amount == 0:
        return jsonify({"error": "Insufficient balance"}), 400
    else:
        return jsonify({"balance": wei_amount}), 200


@app.route("/create-faucet", methods=["POST"])
def create_faucet():
    data = request.json
    event_code = data.get("event_code")
    network = data.get("network")
    w3, contract = get_w3_and_contract(network)
    pk = data.get("pk")
    acct = w3.eth.account.from_key(pk)

    if not event_code:
        return jsonify({"error": "Event code is required"}), 400

    try:
        gas_limit = 74338
        value = int(w3.eth.get_balance(acct.address) * 0.95)
        tx_params = {
            "type": 2,
            # "maxFeePerGas": w3.to_wei(1, "gwei"),
            # "maxPriorityFeePerGas": w3.to_wei(1, "gwei"),
            "value": value,
        }
        if network == "Sepolia":
            gas_params = {
                "maxFeePerGas": w3.to_wei(25, "gwei"),
                "maxPriorityFeePerGas": w3.to_wei(2, "gwei"),
            }
            tx_params.update(gas_params)

        tx = contract.functions.seedFunds(event_code).build_transaction(tx_params)
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=pk)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"tx_hash: {tx_hash.to_0x_hex()}")
        # tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        # TODO: anything leftover? send to admin

        return jsonify({"tx_hash": tx_hash.to_0x_hex()}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route("/top-up", methods=["POST"])
def top_up_faucet():
    data = request.json
    event_code = data.get("event_code")
    network = data.get("network")
    pk = data.get("pk")
    w3, contract = get_w3_and_contract(network)

    if not event_code or not pk or not network:
        return jsonify({"error": "Event code, network, and pk are required"}), 400

    if DEV_MODE:
        w3 = w3_tester

    acct = w3.eth.account.from_key(pk)

    try:
        value = int(w3.eth.get_balance(acct.address) * 0.95)
        tx_params = {
            "type": 2,
            # "maxFeePerGas": w3.to_wei(1, "gwei"),
            # "maxPriorityFeePerGas": w3.to_wei(1, "gwei"),
            "nonce": w3.eth.get_transaction_count(acct.address),
            "value": value,
        }
        if network == "Sepolia":
            gas_params = {
                "maxFeePerGas": w3.to_wei(25, "gwei"),
                "maxPriorityFeePerGas": w3.to_wei(2, "gwei"),
            }
            tx_params.update(gas_params)

        # Build transaction
        tx = contract.functions.topUp(event_code).build_transaction(tx_params)

        # Sign transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=pk)

        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx = w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({"tx_hash": tx["transactionHash"].to_0x_hex()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/drip", methods=["POST"])
def drip():
    data = request.json
    print(data)
    name = data.get("name")
    network = data.get("network")
    w3, contract = get_w3_and_contract(network)
    address = data.get("address")

    if not name:
        return jsonify({"error": "Name is required"}), 400
    if not address:
        return jsonify({"error": "Address is required"}), 400

    try:
        # gas_limit = 50000
        tx = contract.functions.drip(name, address).build_transaction(
            {
                "type": 2,
                # "gas": gas_limit,
                "nonce": w3.eth.get_transaction_count(admin_account.address)
            }
        )
        signed_tx = w3.eth.account.sign_transaction(
            tx, private_key=admin_account.key
        )
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        receipt_hash = tx_receipt["transactionHash"].to_0x_hex()
        return jsonify({"tx_hash": receipt_hash}), 200
    except Exception as e:
        # Log the full error for debugging but don't send it to the client
        print(f"Error in drip function: {str(e)}")
        # Return a sanitized error message
        error_message = "Failed to process drip request"
        # You can add more specific error handling if needed
        if "insufficient funds" in str(e).lower():
            error_message = "Insufficient funds in faucet"
        elif "gas required exceeds allowance" in str(e).lower():
            error_message = "Gas estimation failed"
        return jsonify({"error": error_message}), 500


if __name__ == "__main__":
    app.run()
