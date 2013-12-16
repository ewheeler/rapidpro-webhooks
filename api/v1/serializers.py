import functools
import json

import umsgpack
from flask import Response

import loader
import exceptions


class SerializationError(exceptions.APIError):

    def __init__(self, message=None, serializer=None,
                 operation=None, error=None):
        self.message = message
        self.error = error
        self.serializer = serializer
        self.operation = operation
        if (message is None) and all([operation, serializer]):
            self.message = "Failed to {0} data using {1} serializer".format(
                operation, serializer)


class Serializer(object):

    def encode(self, data):
        "Return serialized verion of a mapping (like dict)"
        raise NotImplementedError("Define in subclass")

    def decode(self, data):
        "Return a python dict"
        raise NotImplementedError("Define in subclass")

    @property
    def content_type(self):
        "Return content type for serialized data"
        raise NotImplementedError("Define in subclass")

    def __unicode__(self):
        return self.content_type.split('/')[-1]

    def from_dict(self, data):
        return self.encode(data)

    def to_dict(self, data):
        return self.decode(data)

    def to_response(self, data):
        return Response(self.encode(data), content_type=self.content_type)


class JsonSerializer(Serializer):

    def _encoder(self):
        # TODO is it useful to have a separate method that returns a callable?
        # this allows us to abstract away serializer-specific args
        return functools.partial(json.dumps,
                                 sort_keys=True, ensure_ascii=False)

    def _decoder(self):
        # TODO is it useful to have a separate method that returns a callable?
        # this allows us to abstract away serializer-specific args
        return functools.partial(json.loads)

    def decode(self, data):
        try:
            return self._decoder()(data)
        except ValueError as err:
            raise SerializationError(serializer='json', operation='decode',
                                     error=err)

    def encode(self, data):
        try:
            return self._encoder()(data)
        except (TypeError, ValueError) as err:
            raise SerializationError(serializer='json', operation='encode',
                                     error=err)

    @property
    def content_type(self):
        return 'application/json'


class MsgpackSerializer(Serializer):

    def _encoder(self):
        # TODO is it useful to have a separate method that returns a callable?
        # this allows us to abstract away serializer-specific args
        return functools.partial(umsgpack.packb)

    def _decoder(self):
        # TODO is it useful to have a separate method that returns a callable?
        # this allows us to abstract away serializer-specific args
        return functools.partial(umsgpack.unpackb)

    def decode(self, data):
        try:
            return self._decoder()(data)
        except TypeError as err:
            raise SerializationError(serializer='msgpack', operation='decode',
                                     error=err)
        except umsgpack.UnpackException as err:
            # TODO catch individual unpack erors?
            # github.com/vsergeev/u-msgpack-python/blob/master/umsgpack.py#L63
            raise SerializationError(serializer='msgpack', operation='decode',
                                     error=err)

    def encode(self, data):
        try:
            return self._encoder()(data)
        except umsgpack.PackException as err:
            # TODO catch individual pack erors?
            # github.com/vsergeev/u-msgpack-python/blob/master/umsgpack.py#L61
            raise SerializationError(serializer='msgpack', operation='encode',
                                     error=err)

    @property
    def content_type(self):
        return 'application/x-msgpack'

# create serializer registry with json as default
registry = loader.Registry(default=JsonSerializer,
                           name='json', register_instance=True)
