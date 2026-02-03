import grpc
from concurrent import futures
import time

# Import the generated Protobuf / gRPC code
from milestone1.proto import grocery_pb2
from milestone1.proto import grocery_pb2_grpc


class InventoryService(grocery_pb2_grpc.InventoryServiceServicer):
    """
    Milestone 1: Inventory receives a gRPC request and replies with success.
    """

    def SubmitOrder(self, request, context):
        # request is an OrderRequest Protobuf message
        print("=== Inventory received request ===")
        print("request_type:", request.request_type)
        print("id:", request.id)
        print("items:", dict(request.items))

        # Always succeed for Milestone 1
        return grocery_pb2.OrderReply(
            code=grocery_pb2.OK,
            message="Inventory: OK (Milestone 1 stub success)"
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grocery_pb2_grpc.add_InventoryServiceServicer_to_server(InventoryService(), server)

    listen_addr = "0.0.0.0:50051"
    server.add_insecure_port(listen_addr)
    server.start()

    print(f"[Inventory gRPC] listening on {listen_addr}")

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("\n[Inventory gRPC] shutting down...")
        server.stop(0)


if __name__ == "__main__":
    serve()
