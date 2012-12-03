from persistent.dict import PersistentDict
from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations

from .interfaces.packet import Ipacket, IpacketDefinition
from genweb.packets import PACKETS_KEY
from genweb.packets import packetsMessageFactory as _


class EstudisUPC(object):
    implements(IpacketDefinition)
    adapts(Ipacket)

    def __init__(self, context):
        self.context = context
        self.title = "Estudis UPC"
        self.description = "Informacio UPC sobre un estudi especific"
        self.URL_schema = 'http://www.upc.edu/grau/fitxa_grau.php?id_estudi=%(id_estudi)s&lang=%(lang)s'
        self.fields = [_(u'id_estudi')]
        annotations = IAnnotations(context)
        self.default = dict([(field, '') for field in self.fields])
        self._info = annotations.setdefault(PACKETS_KEY, PersistentDict(self.default))

    def get_info(self):
        annotations = IAnnotations(self.context)
        self._info = annotations.setdefault(PACKETS_KEY, PersistentDict(self.default))
        return self._info

    def set_info(self, value):
        annotations = IAnnotations(self.context)
        annotations.setdefault(PACKETS_KEY, PersistentDict(self.default))
        annotations[PACKETS_KEY] = value

    info = property(get_info, set_info)
