# Milestone 1 - Client, Ordering, and Inventory

This milestone now implements end-to-end skeleton, including:

- Streamlit web interface client
- Basic Ordering microservice (Flask) using HTTP + JSON
- Basic Inventory microservice (gRPC) using Protobuf

## Directory Structure

```
milestone1/
├── client/
│ ├── app.py               # Streamlit frontend
│ ├── requirements.txt
│ └── README.md
├── ordering/
│ └── app.py               # Flask Ordering service
├── inventory/
│ └── server.py            # gRPC Inventory service
├── proto/
│ ├── grocery.proto        # Protobuf schema
│ ├── grocery_pb2.py
│ ├── grocery_pb2_grpc.py
│ └── init.py
├── init.py
└── README.md              # this file
```

## Technologies Used

- Streamlit frontend
- Ordering Service: Flask + HTTP/JSON
- Inventory Service: gRPC + Protobuf
- Serialization:
  - JSON for HTTP communication
  - Protobuf for gRPC communication
- Deployment Environment: Chameleon Cloud VM (Ubuntu 24.04)
- SSH access with port forwarding (tunneling)

## Setup

### Requirements

Activate the virtual environment:

```
source .venv/bin/activate
```

Install required packages:

```
pip install flask streamlit requests grpcio grpcio-tools protobuf
```

### Run Client

You need three SSH'd terminals

**Terminal 1 - Inventory gRPC Service**

From repository root:

```
source .venv/bin/activate
python milestone1/inventory/server.py
```

Expected output:

```
[Inventory gRPC] listening on 0.0.0.0:50051
```

**Terminal 2 - Ordering Flask Service**

From repository root:

```
source .venv/bin/activate
export INVENTORY_ADDR=localhost:50051
export FLASK_APP=milestone1/ordering/app.py
flask run --host 0.0.0.0 --port 5000
```

Expected output:

```
Running on http://127.0.0.1:5000
```

**Terminal 3 - Streamlit Client**

From repository root:

```
source .venv/bin/activate
pip install -r milestone1/client/requirements.txt
streamlit run milestone1/client/app.py --server.address 0.0.0.0 --server.port 8501
```

Expected output:

```
You can now view your Streamlit app in your browser.
URL: http://0.0.0.0:8501
```

**Open in browser**

Streamlit UI:

http://localhost:8501

Ordering health check:

http://localhost:5000/health

### Use Client

1. Open http://localhost:8501

2. Set Ordering Service URL to:
   ```
   http://localhost:5000/submit
   ```

4. Select request type (`GROCERY_ORDER` or `RESTOCK_ORDER`)

5. Enter Customer/Supplier ID

6. Add item quantities (>0)

7. Click Submit

**Example JSON Output:**

```
{
  "request_type": "GROCERY_ORDER",
  "id": "c101",
  "items": {
    "milk": 2,
    "bread": 1
  }
}
```

**Example result:**

Streamlit display:

```
{
  "code": "OK",
  "message": "Inventory: OK (Milestone 1 stub success)"
}
```

Inventory terminal will also print received request fields.

### Not Implemented Yet (future milestones)

- Database (Postgres)
- Robot microservices
- ZeroMQ + FlatBuffers
- Pricing/nalytics services
- Actual inventory logic

### Notes

Chameleon VM uses private IPs. In this case, a fourth terminal on local machine is needed for SSH port forwarding. Once tunneling is configured, all services can communicate as expected. Explicit details are not currently listed.
