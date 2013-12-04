# should this be an Exception instead?
class ResourceError(RuntimeError):
    pass


class ResourceUnavailableError(ResourceError):

    def __init__(self, resource, message):
        self.resource = resource
        self.message = message


class BaseResource(object):

    def get(self, id, source=None):
        "Retrieve a contact record by ID."
        raise NotImplementedError("Define in subclass")

    def create(self, data):
        "Create a contact record."
        raise NotImplementedError("Define in subclass")

    def update(self, id, data):
        "Update a contact record by ID."
        raise NotImplementedError("Define in subclass")

    def delete(self, id):
        "Delete a contact record."
        raise NotImplementedError("Define in subclass")

    def filter(self, *lookups):
        "Find contact records matching the given lookups."
        raise NotImplementedError("Define in subclass")

    def link(self, id, source_id, source_name):
        "Associated a source/id pair with this contact."
        raise NotImplementedError("Define in subclass")

    def unlink(self, id, source_id, source_name):
        "Remove association of a source/id pair with this contact."
        raise NotImplementedError("Define in subclass")


class ContactBaseResource(BaseResource):

    def administrators(self):
        "List administrators"
        raise NotImplementedError("Define in subclass")


class GroupBaseResource(BaseResource):

    def list(self, source_id, source_name):
        "List all groups."
        raise NotImplementedError("Define in subclass")


class ResourceSourceBase(object):

    def id(self):
        "ID for this resource source"
        raise NotImplementedError("Define in subclass")

    def name(self):
        "Name for this resource source"
        raise NotImplementedError("Define in subclass")

    def deprecated(self):
        "Boolean describing if this source can accept new resources"
        raise NotImplementedError("Define in subclass")
