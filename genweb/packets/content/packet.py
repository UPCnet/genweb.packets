"""Definition of the packet content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from genweb.packets.interfaces import Ipacket
from genweb.packets.config import PROJECTNAME

packetSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))


schemata.finalizeATCTSchema(
    packetSchema,
    folderish=True,
    moveDiscussion=False
)


class packet(folder.ATFolder):
    """A packed content"""
    implements(Ipacket)

    meta_type = "packet"
    schema = packetSchema


atapi.registerType(packet, PROJECTNAME)
