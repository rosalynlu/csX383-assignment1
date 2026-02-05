"""
Helper package init for protoc-generated modules.

grpc_tools sometimes generates imports like:
    import grocery_pb2 as grocery__pb2

When the generated files live inside a package (generated/proto),
that top-level import fails. We fix it by aliasing the packaged
module name into sys.modules so that `import grocery_pb2` resolves.
"""

import sys
from importlib import import_module

# Import the packaged module
_pb2 = import_module("generated.proto.grocery_pb2")

# Alias it so top-level "import grocery_pb2" works
sys.modules.setdefault("grocery_pb2", _pb2)
