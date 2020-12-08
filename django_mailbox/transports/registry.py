registry = {}


def register(transport_type):
    def decorator(f):
        registry[transport_type] = f
        return f
    return decorator
