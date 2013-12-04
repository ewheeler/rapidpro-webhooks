from .base import ResourceSourceBase


class LegacyTrac(ResourceSourceBase):
    pass


class LegacyUreport(LegacyTrac):
    pass


class LegacyMtrac(LegacyTrac):
    pass


class LegacyEdutrac(LegacyTrac):
    pass


class LegacyDevtrac(LegacyTrac):
    pass


class Devtrac(ResourceSourceBase):
    pass


class GsmBackend(ResourceSourceBase):
    pass


class Facebook(ResourceSourceBase):
    pass


class Twitter(ResourceSourceBase):
    pass
