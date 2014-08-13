from zope.interface import Interface
from zope import schema
from plone.app.contenttypes.interfaces import IFolder


class Ipacket(IFolder):
    """Marker interface for the packet"""


class IpacketDefinition(Interface):
    """A packet definition"""

    order = schema.Int(title=u"Order")
    URL_schema = schema.TextLine(title=u"The URL schema of the packet")
