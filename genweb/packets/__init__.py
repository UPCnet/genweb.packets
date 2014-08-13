from zope.i18nmessageid import MessageFactory

_ = packetsMessageFactory = MessageFactory('genweb.packets')

PACKETS_KEY = 'genweb.packets'


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
