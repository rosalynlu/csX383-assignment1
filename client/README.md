## Milestone 1 Streamlit Client

### Install (in your venv)
pip install -r milestone1/client/requirements.txt

### Run
streamlit run milestone1/client/app.py --server.address 0.0.0.0 --server.port 8501

Open in browser:
http://<VM_IP>:8501

### What it sends
POST JSON to Ordering Service URL (default: http://localhost:5000/submit)

{
  "request_type": "GROCERY_ORDER" or "RESTOCK_ORDER",
  "id": "<customer_or_supplier_id>",
  "items": {"milk": 2, "bread": 1}
}
