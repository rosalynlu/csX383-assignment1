Milestone 1 — Streamlit Client (Frontend)

This milestone implements the client frontend for PA1.

The client is a simple Streamlit web interface that allows users to:

- Submit Grocery Orders

- Submit Restock Orders

- Send requests as HTTP + JSON to the Ordering (Flask) service

Directory Structure

milestone1/

│

├── client/

│   └── app.py        # Streamlit frontend client

│

└── README.md         # This file

Requirements

Activate the virtual environment:

source .venv/bin/activate



Install required packages:

pip install streamlit requests

Running the Client

Start the Streamlit frontend:

streamlit run milestone1/client/app.py --server.address 0.0.0.0 --server.port 8501



Open in browser:

http://<VM-IP>:8501

Example: http://192.168.2.2:8501

Using the Client

1. Enter the Ordering Service URL (Flask endpoint)

2. Select request type: GROCERY_ORDER or RESTOCK_ORDER

3. Enter Customer ID or Supplier ID

4. Add item quantities (>0)

5. Click Submit

Example JSON Payload

{

  "request_type": "GROCERY_ORDER",

  "id": "c101",

  "items": {

    "milk": 2,

    "bread": 1

  }

}

Notes

- The Ordering (Flask) backend service must be running separately.

- This milestone only provides the frontend client interface and request formatting.

- The service URL can be changed in the Streamlit app input box.

