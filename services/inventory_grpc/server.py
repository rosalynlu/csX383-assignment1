import os
import time
import uuid
import threading
from concurrent import futures
from typing import Dict, Set

import grpc
import zmq

from generated.proto import grocery_pb2
from generated.proto import grocery_pb2_grpc

# FlatBuffers generated modules
from groceryfb import WorkOrder, RequestType, ItemQty


ZMQ_PUB_ADDR = os.environ.get("ZMQ_PUB_ADDR", "tcp://0.0.0.0:5556")


def build_workorder_fb(request_id: str, request_type: int, served_id: str, items: Dict[str, int]) -> bytes:
    """
    Build FlatBuffers WorkOrder message.
    """
    import flatbuffers

    builder = flatbuffers.Builder(1024)

    # Build ItemQty objects
    item_offsets = []
    for name, qty in items.items():
        name_off = builder.CreateString(name)
        ItemQty.ItemQtyStart(builder)
        ItemQty.ItemQtyAddName(builder, name_off)
        ItemQty.ItemQtyAddQty(builder, int(qty))
        item_offsets.append(ItemQty.ItemQtyEnd(builder))

    WorkOrder.WorkOrderStartItemsVector(builder, len(item_offsets))
    for off in reversed(item_offsets):
        builder.PrependUOffsetTRelative(off)
    items_vec = builder.EndVector()

    rid_off = builder.CreateString(request_id)
    sid_off = builder.CreateString(served_id)

    WorkOrder.WorkOrderStart(builder)
    WorkOrder.WorkOrderAddRequestId(builder, rid_off)
    WorkOrder.WorkOrderAddRequestType(builder, request_type)
    WorkOrder.WorkOrderAddId(builder, sid_off)
    WorkOrder.WorkOrderAddItems(builder, items_vec)
    wo = WorkOrder.WorkOrderEnd(builder)

    builder.Finish(wo)
    return bytes(builder.Output())


class RobotTracker:
    """
    Tracks which robots have responded for a given request_id.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._waiters: Dict[str, threading.Event] = {}
        self._seen: Dict[str, Set[str]] = {}

    def init_request(self, request_id: str):
        with self._lock:
            self._waiters[request_id] = threading.Event()
            self._seen[request_id] = set()

    def mark_robot(self, request_id: str, robot_name: str, expected_count: int):
        with self._lock:
            if request_id not in self._seen:
                return
            self._seen[request_id].add(robot_name)
            if len(self._seen[request_id]) >= expected_count:
                self._waiters[request_id].set()

    def wait_all(self, request_id: str, timeout_s: float) -> bool:
        with self._lock:
            ev = self._waiters.get(request_id)
        if not ev:
            return False
        return ev.wait(timeout=timeout_s)

    def cleanup(self, request_id: str):
        with self._lock:
            self._waiters.pop(request_id, None)
            self._seen.pop(request_id, None)


class InventoryService(grocery_pb2_grpc.InventoryServiceServicer):
    """
    Milestone 2:
    - Receives gRPC order from Ordering
    - Publishes FlatBuffers WorkOrder to robots via ZeroMQ PUB/SUB
    - Receives RobotResult callbacks via gRPC
    - Waits for all 5 robot responses, then replies OK
    """
    EXPECTED_ROBOTS = {"bread", "dairy", "meat", "produce", "party"}

    def __init__(self, zmq_pub_socket, tracker: RobotTracker):
        self.pub = zmq_pub_socket
        self.tracker = tracker

    def SubmitOrder(self, request, context):
        # Validate non-empty items (spec says message cannot be empty)
        if not request.id or len(request.items) == 0:
            return grocery_pb2.OrderReply(code=grocery_pb2.BAD_REQUEST, message="Empty id or items")

        request_id = str(uuid.uuid4())
        served_id = request.id

        print(f"\n=== Inventory received order request_id={request_id} type={request.request_type} id={served_id} ===")
        items_dict = dict(request.items)
        print("items:", items_dict)

        # Prepare to wait for robots
        self.tracker.init_request(request_id)

        # Determine topic: FETCH for grocery, RESTOCK for restock (per spec)
        topic = b"FETCH" if request.request_type == grocery_pb2.GROCERY_ORDER else b"RESTOCK"

        # Build FlatBuffers payload and publish
        fb_type = RequestType.RequestType.GROCERY_ORDER if topic == b"FETCH" else RequestType.RequestType.RESTOCK_ORDER
        payload = build_workorder_fb(request_id, fb_type, served_id, items_dict)

        self.pub.send_multipart([topic, payload])
        print(f"[Inventory] Published {topic.decode()} via ZMQ to robots on {ZMQ_PUB_ADDR}")

        # Wait for all 5 robots to respond (timeout to avoid hanging forever)
        ok = self.tracker.wait_all(request_id, timeout_s=10.0)
        if not ok:
            self.tracker.cleanup(request_id)
            return grocery_pb2.OrderReply(code=grocery_pb2.BAD_REQUEST, message="Timed out waiting for all robots")

        self.tracker.cleanup(request_id)
        return grocery_pb2.OrderReply(code=grocery_pb2.OK, message=f"OK: received all robot replies for {request_id}")

    def ReportRobotResult(self, request, context):
        # request is RobotResult
        print(f"[Inventory] RobotResult request_id={request.request_id} robot={request.robot_name} "
              f"served_id={request.served_id} status={request.status} msg={request.message}")

        # Mark robot as seen
        self.tracker.mark_robot(request.request_id, request.robot_name, expected_count=len(self.EXPECTED_ROBOTS))

        return grocery_pb2.Ack(ok=True, message="ack")


def serve():
    # ZeroMQ PUB socket
    ctx = zmq.Context.instance()
    pub = ctx.socket(zmq.PUB)
    pub.bind(ZMQ_PUB_ADDR)
    print(f"[Inventory] ZMQ PUB bound at {ZMQ_PUB_ADDR}")

    tracker = RobotTracker()

    # gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grocery_pb2_grpc.add_InventoryServiceServicer_to_server(InventoryService(pub, tracker), server)

    grpc_addr = "0.0.0.0:50051"
    server.add_insecure_port(grpc_addr)
    server.start()
    print(f"[Inventory gRPC] listening on {grpc_addr}")

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("\n[Inventory] shutting down...")
        server.stop(0)
        pub.close()


if __name__ == "__main__":
    serve()
