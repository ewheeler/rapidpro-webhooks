import operator
import re
import socket

from flask import request, url_for

from unidecode import unidecode

from rapidpro_webhooks.apps.core import exceptions
from rapidpro_webhooks.apps.core.serializers import registry

# serializer content types (e.g., 'application/json')
SERIALIZER_TYPES = [registry.get(c[0]).content_type for c in registry.choices]
# serializer formats (e.g., 'json')
SERIALIZER_FORMATS = map(operator.itemgetter(0), registry.choices)

# e.g., {'json': 'application/json'}
SERIALIZER_FORMATS_MAP = dict(zip(SERIALIZER_FORMATS, SERIALIZER_TYPES))
# e.g., {'application/json': 'json'}
SERIALIZER_TYPES_MAP = {v: k for k, v in SERIALIZER_FORMATS_MAP.items()}


def is_serializer_registered(serializer_slug):
    return serializer_slug in SERIALIZER_FORMATS


def serialize_data_to_response(data=None, serializer_slug=None):
    """ given an API response serializer/format type, serializes
        data (a mapping like dict) into the given format.
        serializer_slug can be either the format name (e.g., 'json')
        or the response content type describing that format
        (e.g., 'application/json').
        Returns a flask Response object containing serialized data
        and the corresponding content_type
    """
    if serializer_slug is None:
        serializer_slug = registry.default.content_type

    try:
        assert (serializer_slug in SERIALIZER_FORMATS or serializer_slug in SERIALIZER_TYPES)
    except AssertionError:
        raise exceptions.APIError(code=422,
                                  message='invalid serialization format',
                                  field=serializer_slug,
                                  resource='serializer')

    if serializer_slug in SERIALIZER_FORMATS:
        return registry.get(serializer_slug).to_response(data)
    else:
        return registry.get(SERIALIZER_TYPES_MAP[serializer_slug])\
            .to_response(data)


def create_response(response_data):
    """ Convenience method to serialize a python dict to
        json or msgpack based on request's `format` argument
        TODO should this live elsewhere? in api.py?
    """
    # if request includes format argument, get it.
    serializer_slug = request.values.get('format')

    if serializer_slug is not None:
        # `format` is not required, so if an unregisterd format is
        # requested then this will raise an exception and return a 422.
        # Also, even if headers indicate a different content type,
        # the explicitly passed format arg will be preferred.
        return serialize_data_to_response(data=response_data,
                                          serializer_slug=serializer_slug)

    # if format is not explicitly given as an arg, look at request headers
    mimes = request.accept_mimetypes  # shorthand to prevent lines > 79 chars
    best = mimes.best_match(SERIALIZER_TYPES)

    # Why check if msgpack has a higher quality than default and not just
    # go with the best match? Because some browsers accept on */* and
    # we don't want to deliver msgpack to anything not asking for it.
    # TODO if request header accepts msgpack but serializer is not registered,
    # we will silently return json instead of an error
    if is_serializer_registered('msgpack'):
        if (best == registry.get('msgpack').content_type) \
                and (mimes[best] > mimes[registry.default.content_type]):
            serializer_slug = best

    return serialize_data_to_response(data=response_data,
                                      serializer_slug=serializer_slug)


def rule_link(url_rule):
    # TODO should this live elsewhere? in api.py?
    # http://en.wikipedia.org/wiki/HATEOAS
    return {"title": url_rule.endpoint.split('.')[-1],
            "href": url_for(url_rule.endpoint, _external=True),
            "methods": list(url_rule.methods)}


def only_digits(text):
    result = ""
    if isinstance(text, str):
        result = re.sub(r"\D", "", text)
    return result


# this linked regex will actually validated all valid address based on RFC 822
# http://www.ex-parrot.com/~pdw/Mail-RFC822-Address.html
# however this is crazy...
# instead, the following regex will match most of them
# from http://code.activestate.com/recipes/66439-stringvalidator/?in=user-114221#c14
# matches "Bob_O'Reilly+tag@example.com" and "a@b.dk"
# but not "foobar@dk" (which a valid, working address)
_email_pat = re.compile(r"^[^\s]+@[^\s]+\.[^\s]{2,3}$")


def is_possible_email(email_str):
    if not isinstance(email_str, str):
        return False
    email_str = email_str.strip()
    if _email_pat.search(email_str) is None:
        return False
    return True


# asking socket to validate an ip address
# is allegedly faster than using a regex
# http://www.seanelavelle.com/2012/04/16/checking-for-a-valid-ip-in-python/
def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True


def is_valid_ipv6_address(address):
    try:
        socket.inet_pton(socket.AF_INET6, address)
    except socket.error:  # not a valid address
        return False
    return True


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug.
       Graciously cribbed from http://flask.pocoo.org/snippets/5/ """
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return str(delim.join(result))
