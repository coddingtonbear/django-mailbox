transport_registry = {}


def register_transport(transport_type):
    def decorator(f):
        transport_registry[transport_type] = f
        return f
    return decorator
