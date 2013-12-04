from .base import GroupBaseResource


class GroupResource(GroupBaseResource):

    def list(self):
        return [{'name': 'scouts',
                 'source_name': 'ureport'},
                {'name': 'doctors',
                 'source_name': 'mtrac'},
                {'name': 'MPs',
                 'source_name': 'ureport'},
                {'name': 'teachers',
                 'source_name': 'edutrac'}]
