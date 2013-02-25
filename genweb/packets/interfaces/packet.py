from zope.interface import Interface
from zope import schema


class Ipacket(Interface):
    """Marker interface for the packet"""


class IpacketDefinition(Interface):
    """A packet definition"""

    URL_schema = schema.TextLine(title=u"The URL schema of the packet")
