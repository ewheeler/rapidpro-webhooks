import operator

from serializers import registry
import exceptions


# serializer content types (e.g., 'application/json')
SERIALIZER_TYPES = [registry.get(c[0]).content_type for c in registry.choices]
# serializer formats (e.g., 'json')
SERIALIZER_FORMATS = map(operator.itemgetter(0), registry.choices)

# e.g., {'json': 'application/json'}
SERIALIZER_FORMATS_MAP = dict(zip(SERIALIZER_FORMATS, SERIALIZER_TYPES))
# e.g., {'application/json': 'json'}
SERIALIZER_TYPES_MAP = {v: k for k, v in SERIALIZER_FORMATS_MAP.iteritems()}


def is_serializer_registered(serializer_slug):
    return serializer_slug in SERIALIZER_FORMATS


def serialize_data_to_response(data=None, serializer_slug=None):
    """ given an API response serializer/format type, serializes
        data (a mapping like dict) into the given format.
        serializer_slug can be either the format name (e.g., 'json')
        or the response content type describing that format
        (e.g., 'application/json')
    """
    if serializer_slug is None:
        serializer_slug = registry.default.content_type

    try:
        assert (serializer_slug in SERIALIZER_FORMATS
                or serializer_slug in SERIALIZER_TYPES)
    except AssertionError:
        raise exceptions.APIError(code=422,
                                  message='invalid response format',
                                  field=serializer_slug,
                                  resource='response format')
    try:
        assert data is not None
    except AssertionError:
        # TODO
        pass
    if serializer_slug in SERIALIZER_FORMATS:
        return registry.get(serializer_slug).to_response(data)
    else:
        return registry.get(SERIALIZER_TYPES_MAP[serializer_slug]).to_response(data)
