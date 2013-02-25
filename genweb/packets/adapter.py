from persistent.dict import PersistentDict
from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations

from .interfaces import Ipacket, IpacketDefinition
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
        self.default = dict([(field, '') for field in self.fields])
        annotations = IAnnotations(context)
        self._packet_fields = annotations.setdefault(PACKETS_KEY + '.fields', PersistentDict(self.default))
        self._type = annotations.setdefault(PACKETS_KEY + '.type', '')

    def get_packet_fields(self):
        annotations = IAnnotations(self.context)
        self._packet_fields = annotations.setdefault(PACKETS_KEY + '.fields', PersistentDict(self.default))
        return self._packet_fields

    def set_packet_fields(self, value):
        annotations = IAnnotations(self.context)
        annotations.setdefault(PACKETS_KEY + '.fields', PersistentDict(self.default))
        annotations[PACKETS_KEY + '.fields'] = value

    packet_fields = property(get_packet_fields, set_packet_fields)

    def get_packet_type(self):
        annotations = IAnnotations(self.context)
        self._type = annotations.setdefault(PACKETS_KEY + '.type', '')
        return self._type

    def set_packet_type(self, value):
        annotations = IAnnotations(self.context)
        annotations.setdefault(PACKETS_KEY + '.type', '')
        annotations[PACKETS_KEY + '.type'] = value

    packet_type = property(get_packet_type, set_packet_type)
