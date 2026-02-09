import os
import sys
import time
from concurrent import futures

import grpc

# Add path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from generated.proto import grocery_pb2
from generated.proto import grocery_pb2_grpc

# Database helper
from utils.db import get_db_connection


class PricingService(grocery_pb2_grpc.PricingServiceServicer):
    """
    Pricing microservice that calculates bills for grocery orders.
    Queries the pricing database table to get item prices.
    """

    def GetPrice(self, request, context):
        """
        Calculate total price for requested items.

        Args:
            request: PriceRequest with map of item_name -> quantity

        Returns:
            PriceReply with itemized prices and total
        """
        items_dict = dict(request.items)

        if not items_dict:
            return grocery_pb2.PriceReply(
                code=grocery_pb2.BAD_REQUEST,
                message="No items to price",
                total=0.0
            )

        print(f"[Pricing] Calculating price for items: {items_dict}")

        try:
            with get_db_connection() as conn:
                cur = conn.cursor()

                item_prices = []
                total = 0.0

                for item_name, quantity in items_dict.items():
                    # Get the most recent price for this item
                    cur.execute("""
                        SELECT p.price
                        FROM pricing p
                        JOIN items i ON p.item_id = i.id
                        WHERE i.name = %s
                        ORDER BY p.effective_date DESC
                        LIMIT 1
                    """, (item_name,))

                    row = cur.fetchone()

                    if not row:
                        print(f"[Pricing] Warning: No price found for item '{item_name}', using $0.00")
                        unit_price = 0.0
                    else:
                        unit_price = float(row[0])

                    subtotal = unit_price * quantity
                    total += subtotal

                    # Create ItemPrice message
                    item_price = grocery_pb2.ItemPrice(
                        name=item_name,
                        quantity=quantity,
                        unit_price=unit_price,
                        subtotal=subtotal
                    )
                    item_prices.append(item_price)

                    print(f"[Pricing]   {item_name}: {quantity} x ${unit_price:.2f} = ${subtotal:.2f}")

                print(f"[Pricing] Total: ${total:.2f}")

                return grocery_pb2.PriceReply(
                    code=grocery_pb2.OK,
                    message=f"Price calculated for {len(items_dict)} items",
                    item_prices=item_prices,
                    total=total
                )

        except Exception as e:
            print(f"[Pricing] Error: {e}")
            return grocery_pb2.PriceReply(
                code=grocery_pb2.BAD_REQUEST,
                message=f"Pricing error: {e}",
                total=0.0
            )


def serve():
    """Start the Pricing gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grocery_pb2_grpc.add_PricingServiceServicer_to_server(PricingService(), server)

    grpc_addr = "0.0.0.0:50053"
    server.add_insecure_port(grpc_addr)
    server.start()
    print(f"[Pricing gRPC] listening on {grpc_addr}")

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("\n[Pricing] shutting down...")
        server.stop(0)


if __name__ == "__main__":
    serve()
