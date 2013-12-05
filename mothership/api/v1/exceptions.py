from werkzeug.exceptions import HTTPException


class APIError(HTTPException):

    def __init__(self, response=None, code=400, field='unknown',
                 resource='unknown', message='Bad request'):
        self.response = response
        self.code = code
        self.field = field
        self.message = message
        self.resource = resource


class RateLimitError(APIError):

    def __init__(self, response=None, code=429, field='unknown',
                 resource='unknown', message='Too Many Requests'):
        self.response = response
        self.code = code
        self.field = field
        self.message = message
        self.resource = resource
