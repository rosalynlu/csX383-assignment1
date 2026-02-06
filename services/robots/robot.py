import argparse
import os
import time
import random

import grpc
import zmq

from generated.proto import grocery_pb2
from generated.proto import grocery_pb2_grpc

# FlatBuffers generated modules
from groceryfb import WorkOrder


CATEGORY_ITEMS = {
    "bread": {"bread"},
    "dairy": {"milk", "eggs"},
    "meat": {"chicken", "beef"},
    "produce": {"apples", "bananas"},
    "party": {"soda", "napkins"},
}


def parse_workorder(buf: bytes):
    wo = WorkOrder.WorkOrder.GetRootAsWorkOrder(buf, 0)
    request_id = wo.RequestId().decode()
    served_id = wo.Id().decode()
    # RequestType is numeric enum in FB; we only need topic from ZMQ for behavior
    items = {}
    for i in range(wo.ItemsLength()):
        it = wo.Items(i)
        name = it.Name().decode()
        qty = int(it.Qty())
        items[name] = qty
    return request_id, served_id, items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="robot name: bread/dairy/meat/produce/party")
    ap.add_argument("--sub_addr", default=os.environ.get("ZMQ_SUB_ADDR", "tcp://127.0.0.1:5556"))
    ap.add_argument("--inventory_addr", default=os.environ.get("INVENTORY_ADDR", "127.0.0.1:50051"))
    args = ap.parse_args()

    robot_name = args.name
    if robot_name not in CATEGORY_ITEMS:
        raise SystemExit(f"Unknown robot name {robot_name}. Choose one of {list(CATEGORY_ITEMS.keys())}")

    my_items = CATEGORY_ITEMS[robot_name]

    # ZMQ SUB
    ctx = zmq.Context.instance()
    sub = ctx.socket(zmq.SUB)
    sub.connect(args.sub_addr)
    sub.setsockopt(zmq.SUBSCRIBE, b"FETCH")
    sub.setsockopt(zmq.SUBSCRIBE, b"RESTOCK")
    print(f"[{robot_name}] Connected SUB to {args.sub_addr} (topics: FETCH, RESTOCK)")

    # gRPC stub
    channel = grpc.insecure_channel(args.inventory_addr)
    stub = grocery_pb2_grpc.InventoryServiceStub(channel)
    print(f"[{robot_name}] gRPC connected to Inventory at {args.inventory_addr}")

    while True:
        topic, payload = sub.recv_multipart()
        topic_s = topic.decode()

        request_id, served_id, items = parse_workorder(payload)
        relevant = {k: v for k, v in items.items() if k in my_items}

        if not relevant:
            # No-op case (spec: if robot has no item to work on, it sends no-op)
            rr = grocery_pb2.RobotResult(
                request_id=request_id,
                served_id=served_id,
                robot_name=robot_name,
                status=grocery_pb2.ROBOT_NOOP,
                message=f"NOOP for topic={topic_s}"
            )
            stub.ReportRobotResult(rr, timeout=5)
            print(f"[{robot_name}] NOOP request_id={request_id} served_id={served_id}")
            continue

        # Simulate work: sleep once per unique item (spec allows sleep)
        for item_name in relevant.keys():
            t = random.uniform(0.2, 0.6)
            print(f"[{robot_name}] Working on {item_name} (sleep {t:.2f}s)")
            time.sleep(t)

        # Simulate time to deliver/restock at cart/shelf
        time.sleep(random.uniform(0.2, 0.5))

        rr = grocery_pb2.RobotResult(
            request_id=request_id,
            served_id=served_id,   # spec: must indicate which customer/supplier it served
            robot_name=robot_name,
            status=grocery_pb2.ROBOT_OK,
            message=f"OK handled {list(relevant.keys())} topic={topic_s}"
        )
        stub.ReportRobotResult(rr, timeout=5)
        print(f"[{robot_name}] OK sent request_id={request_id} served_id={served_id} items={list(relevant.keys())}")


if __name__ == "__main__":
    main()
