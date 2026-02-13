import os
from flask import Flask, request, jsonify
import grpc
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the generated Protobuf / gRPC code
from generated.proto import grocery_pb2
from generated.proto import grocery_pb2_grpc


app = Flask(__name__)

# Inventory gRPC address (use env var or default)
INVENTORY_ADDR = os.environ.get("INVENTORY_ADDR", "localhost:50051")


def parse_request_type(rt: str):
    """
    Convert incoming JSON request_type string to Protobuf enum value.
    """
    if rt == "GROCERY_ORDER":
        return grocery_pb2.GROCERY_ORDER
    if rt == "RESTOCK_ORDER":
        return grocery_pb2.RESTOCK_ORDER
    return None


@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json(force=True)  # Streamlit sends JSON

    # Validation
    req_type_str = str(data.get("request_type", "")).strip()
    id_value = str(data.get("id", "")).strip()
    items = data.get("items", {})

    if not req_type_str or parse_request_type(req_type_str) is None:
        return jsonify({"code": "BAD_REQUEST", "message": "Invalid or missing request_type"}), 400

    if not id_value:
        return jsonify({"code": "BAD_REQUEST", "message": "Missing id"}), 400

    if not isinstance(items, dict) or len(items) == 0:
        return jsonify({"code": "BAD_REQUEST", "message": "Items cannot be empty"}), 400

    # Build Protobuf request
    pb_req = grocery_pb2.OrderRequest(
        request_type=parse_request_type(req_type_str),
        id=id_value,
        items={k: int(v) for k, v in items.items()}
    )

    # Call Inventory via gRPC
    try:
        with grpc.insecure_channel(INVENTORY_ADDR) as channel:
            stub = grocery_pb2_grpc.InventoryServiceStub(channel)
            pb_resp = stub.SubmitOrder(pb_req, timeout=20)

        # Convert Protobuf reply to JSON
        code_str = "OK" if pb_resp.code == grocery_pb2.OK else "BAD_REQUEST"
        return jsonify({
            "code": code_str,
            "message": pb_resp.message
        }), 200

    except Exception as e:
        return jsonify({"code": "BAD_REQUEST", "message": f"gRPC call failed: {e}"}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "inventory_addr": INVENTORY_ADDR})
