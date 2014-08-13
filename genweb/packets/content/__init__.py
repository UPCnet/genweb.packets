from zope.interface import implements

from plone.dexterity.content import Container
from genweb.packets.interfaces import Ipacket


class Packet(Container):
    implements(Ipacket)
