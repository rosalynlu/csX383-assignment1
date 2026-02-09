# csX383-assignment1

This repository contains the implementation of Programming Assignment 1 for CSX383 using a microservice architecture.

- Streamlit web interface client
- Flask + HTTP/JSON ordering microservice
- gRPC + Protobuf inventory microservice
- ZeroMQ pub-sub + FlatBuffers payload robots and gRPC/Protobuf responses
  - Inventory publishes FETCH/RESTOCK topic via FlatBuffers payload
  - Robots subscribe and respond back to the inventory via gRPC

## Repository Structure

```
csX383-assignment/
├── client/
│ ├── __init__.py
│ └── requirements.txt
├── flatbuffers_local/
│ ├── __init__.py
│ └── work.fbs
├── generated/
│ ├── flatbuffers/
│ │ ├── __init__.py              # FlatBuffers generated Python modules
│ ├── proto/
│ │ ├── __init__.py
│ │ ├── grocery_pb2.py
│ │ └── grocery_pb2_grpc.py
│ └── __init__.py
├── groceryfb/
│ ├── ItemQty.py
│ ├── RequestType.py
│ ├── WorkOrder.py
│ └── __init__.py
├── ordering/
│ └── __init__.py
├── proto/
│ ├── __init__.py
│ ├── proto/grocery_pb2.py
│ └── proto/grocery_pb2_grpc.py
├── schemas/
│ ├── flatbuffers/
│ │ └── work.fbs                 # FlatBuffers schema (Inventory -> Robots)
│ ├── proto/
│ │ ├── grocery.proto            # Protobuf schema (Ordering <-> Inventory + Robot -> Inventory)
│ │ └── robots.proto
├── services/
│ ├── client_streamlit/
│ │ └── app.py                   # Streamlit frontend
│ ├── inventory_grpc/
│ │ ├── __init__.py
│ │ └── server.py                # Inventory gRPC server + ZeroMQ PUB
│ ├── ordering_flask/
│ │ └── app.py                   # Flask Ordering service (HTTP/JSON -> gRPC)
│ ├── robots/
│ │ └── robot.py                 # Robot worker (run 5 times with different --name)
├── .gitignore
└── README.md                    # This file
```

## Technologies Used

- Streamlit frontend
- Ordering Service: Flask + HTTP/JSON
- Inventory Service: gRPC + Protobuf
- Robot Communication:
  - Inventory -> Robots: ZeroMQ PUB/SUB + FlatBuffers
  - Robots -> Inventory: gRPC + Protobuf
- Deployment Environment: Chameleon Cloud VM (Ubuntu 24.04)
- Access Method: SSH with port forwarding (tunneling)

## Setup

### Requirements

SSH into the VM from your local machine (using your SSH config + bastion setup)

Activate the virtual environment:

```
source .venv/bin/activate
```

Install required packages:

```
pip install flask streamlit requests grpcio grpcio-tools protobuf pyzmq flatbuffers psycopg2-binary
```
OR
```
pip install -r client/requirements.txt
```

Install FlatBuffers compiler (flatc):

```
sudo apt update
sudo apt install -y flatbuffers-compiler
flatc --version
```

### Database Setup

Install PostgreSQL:

```
sudo apt update
sudo apt install -y postgresql postgresql-contrib
```

Start PostgreSQL service:

```
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

Create database user (use password from .env.example):

```
sudo -u postgres createuser -s admin
```

Copy environment configuration:

```
cp .env.example .env
```

Initialize database:

```
bash scripts/init_db.sh
```

Expected output:

```
Database initialized and seeded
```

### Run Client

You qill run Inventory, 5 robots, Ordering, and Streamlit on eight SSH'd terminals

**Terminal 1 - Inventory (gRPC + ZeroMQ PUB)**

From repository root:

```
source .venv/bin/activate
python services/inventory_grpc/server.py
```

Expected output:

```
[Inventory] ZMQ PUB bound at tcp://0.0.0.0:5556
[Inventory gRPC] listening on 0.0.0.0:50051
```

**Terminala 2-6 - Robots (5 separate processes)**

Run one command per terminal, each from repository root:

```
source .venv/bin/activate
python services/robots/robot.py --name bread
```

```
source .venv/bin/activate
python services/robots/robot.py --name dairy
```

```
source .venv/bin/activate
python services/robots/robot.py --name meat
```

```
source .venv/bin/activate
python services/robots/robot.py --name produce
```

```
source .venv/bin/activate
python services/robots/robot.py --name party
```

Expected outputs:

```
[bread] Connected SUB to tcp://127.0.0.1:5556 (topics: FETCH, RESTOCK)
[bread] gRPC connected to Inventory at 127.0.0.1:50051
```

```
[dairy] Connected SUB to tcp://127.0.0.1:5556 (topics: FETCH, RESTOCK)
[dairy] gRPC connected to Inventory at 127.0.0.1:50051
```

```
[meat] Connected SUB to tcp://127.0.0.1:5556 (topics: FETCH, RESTOCK)
[meat] gRPC connected to Inventory at 127.0.0.1:50051
```

```
[produce] Connected SUB to tcp://127.0.0.1:5556 (topics: FETCH, RESTOCK)
[produce] gRPC connected to Inventory at 127.0.0.1:50051
```

```
[party] Connected SUB to tcp://127.0.0.1:5556 (topics: FETCH, RESTOCK)
[party] gRPC connected to Inventory at 127.0.0.1:50051
```

**Terminal 7 - Ordering (Flask)**

From repository root:

```
source .venv/bin/activate
export INVENTORY_ADDR=127.0.0.1:50051
export FLASK_APP=services/ordering_flask/app.py
flask run --host 0.0.0.0 --port 5000
```

Expected output:

```
 * Serving Flask app 'services/ordering_flask/app.py'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://172.16.6.226:5000
Press CTRL+C to quit
```

**Terminal 8 - Streamlit Client**

From repository root:

```
source .venv/bin/activate
streamlit run services/client_streamlit/app.py --server.address 0.0.0.0 --server.port 8501
```

Expected output:

```
Collecting usage statistics. To deactivate, set browser.gatherUsageStats to false.


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

6. Add item quantities (>0) across multiple aisles

7. Click Submit

**Example JSON payload:**

```
{
  "request_type":"GROCERY_ORDER"
  "id":"abc123"
  "items":{
    "bread":1
    "milk":1
    "beef":1
    "apples":2
    "napkins":1
  }
}
```

**Example Streamlit display:**

```
HTTP status: 200
```

**Example JSON response:**

```
{
  "code":"OK"
  "message":"OK: received all robot replies for 3a31108f-a986-40b8-8bde-2ea8043e1ddd"
}
```

Inventory terminal logs will show that it:
- receives gRPC request
- publishes FETCH via ZeroMQ
- receives 5 robot gRPC responses (ROBOT_OK or ROBOT_NOOP)

Robot terminals will also log their received message and response.

**Example:**

```
[bread] Working on bread (sleep 0.50s)
[bread] OK sent request_id=3a31108f-a986-40b8-8bde-2ea8043e1ddd served_id=abc123 items=['bread']
```

```
[dairy] Working on milk (sleep 0.58s)
[dairy] OK sent request_id=3a31108f-a986-40b8-8bde-2ea8043e1ddd served_id=abc123 items=['milk']
```

```
[meat] Working on beef (sleep 0.46s)
[meat] OK sent request_id=3a31108f-a986-40b8-8bde-2ea8043e1ddd served_id=abc123 items=['beef']
```

```
[produce] Working on apples (sleep 0.33s)
[produce] OK sent request_id=3a31108f-a986-40b8-8bde-2ea8043e1ddd served_id=abc123 items=['apples']
```

```
[party] Working on napkins (sleep 0.52s)
[party] OK sent request_id=3a31108f-a986-40b8-8bde-2ea8043e1ddd served_id=abc123 items=['napkins']
```

```
127.0.0.1 - - [06/Feb/2026 01:02:59] "POST /submit HTTP/1.1" 200 -
```

### Milestones

Milestone 1 implemented an end-to-end skeleton with the web interface client and basic ordering/inventory microservices.

Milestone 2 implemented robot microservices and the messaging pipeline.

> Not Implemented Yet (future milestones):
> - Updated Streamlit UI (currently is outdated and the interface as Milestone 1)
> - Milestone 3:
>   - Full implementation
>   - Actual inventory logic
>   - Pricing microservice integration
>   - Inventory database integration (Postgres)
>   - Data collection analytics and plots
>   - Cloud multi-VM deployment
>   - Demo and video explanation

### Notes

Chameleon VM uses private IPs. Depending on factors like other OS processes listening on/SSH unable to bind (or binding inconsistently) to relevant ports, you may run into issues trying to launch the Streamlit UI from your localhost.

In this case, a ninth terminal on local machine may be needed for SSH port forwarding. If you are on the same SSH config, host alias, and bastion/jump setup/key file, you can directly use the following command.

```
ssh -N -L 8501:127.0.0.1:8501 -L 5000:127.0.0.1:5000 team-ras
```

If you aren't, you can alternatively use this:

```
ssh -N -J bastion-host cc@172.16.6.226 \
  -L 8501:127.0.0.1:8501 \
  -L 5000:127.0.0.1:5000
```

where ```bastion-host``` is the bastion alias or IP, and ```cc@172.16.6.226``` is the VM user and private IP.

From here, the rest of the instructions are the same.
