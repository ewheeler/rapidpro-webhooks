import functools
import json

import umsgpack


def get_serializer(response_format='json'):
    """ given an API response format, returns a tuple consisting of
        (serializer_function, 'content type')
    """
    assert response_format in ['json', 'msgpack']
    if response_format == 'json':
        return (functools.partial(json.dumps), 'application/json')
    else:
        return (functools.partial(umsgpack.packb), 'application/x-msgpack')
