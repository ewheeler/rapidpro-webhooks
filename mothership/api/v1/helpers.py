import functools
import json

import umsgpack

import exceptions


RESPONSE_FORMATS = frozenset(['JSON', 'MSGPACK'])


def get_serializer(response_format='JSON'):
    """ given an API response format, returns a tuple consisting of
        (serializer_function, 'content type')
    """
    try:
        assert response_format in RESPONSE_FORMATS
    except AssertionError:
        raise exceptions.APIError(code=422,
                                  message='invalid response format',
                                  field=response_format,
                                  resource=response_format)

    if response_format == 'JSON':
        return (functools.partial(json.dumps), 'application/json')
    else:
        return (functools.partial(umsgpack.packb), 'application/x-msgpack')
