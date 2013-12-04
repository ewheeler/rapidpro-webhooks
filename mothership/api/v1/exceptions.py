

# should this be an Exception instead?
class APIError(RuntimeError):

    def __init__(self, field, resource, message):
        self.field = field
        self.message = message
        self.resource = resource
