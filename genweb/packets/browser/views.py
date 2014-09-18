from zope.component import getAdapter, getAdapters
from zope.annotation.interfaces import IAnnotations

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from genweb.core import utils
from genweb.packets.interfaces import IpacketDefinition
from genweb.packets import PACKETS_KEY
from genweb.packets import packetsMessageFactory as _

from pyquery import PyQuery as pq

import plone.api
import re
import requests


class packetView(BrowserView):

    template = ViewPageTemplateFile('templates/view.pt')

    def __call__(self):
        return self.template()

    def getType(self):
        annotations = IAnnotations(self.context)
        return annotations.get(PACKETS_KEY + '.type', None)

    def isAlreadyConfigured(self):
        annotations = IAnnotations(self.context)
        if annotations.get(PACKETS_KEY + '.type', None):
            return True
        else:
            return False

    def show_extended_info(self):
        user = plone.api.user.get_current()
        if user.name == 'Anonymous User':
            return False

        user_roles = set(plone.api.user.get_roles(user=user, obj=self.context) +
                         plone.api.user.get_roles(user=user))

        if 'Manager' in user_roles or \
           'WebMaster' in user_roles or \
           'Site Administrator' in user_roles or \
           'Owner' in user_roles:
            return True
        else:
            return False

    def selectedPacket(self):
        annotations = IAnnotations(self.context)
        packet_key = annotations.get(PACKETS_KEY + '.type')
        packet_fields = annotations.get(PACKETS_KEY + '.fields')
        packet_mapui = annotations.get(PACKETS_KEY + '.mapui')

        return dict(packet_key=packet_key, value=packet_fields.get(packet_mapui.get('codi')))

    def getPacket(self):
        packet_type = self.getType()
        adapter = getAdapter(self.context, IpacketDefinition, packet_type)
        adapter.packet_fields.update({'lang': utils.pref_lang()})
        url = adapter.URL_schema % adapter.packet_fields
        raw_html = requests.get(url)
        clean_html = re.sub(r'[\n\r]?', r'', raw_html.content.decode('utf-8'))
        doc = pq(clean_html)
        match = re.search(r'This page does not exist', clean_html)
        if match:
            return _(u"ERROR: Unknown identifier. This page does not exist.")
        else:
            return doc('#content').outerHtml()

    def getTitle(self):
        return self.context.Title()


class packetEdit(BrowserView):

    template = ViewPageTemplateFile('templates/edit.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.available_ptypes = sorted([adapter for adapter in getAdapters((self.context,), IpacketDefinition)], key=lambda adapter: adapter[1].order)

    def __call__(self):
        if self.request.form:
            form = self.request.form
            packet_type = form.get("packet_type")
            adapter = getAdapter(self.context, IpacketDefinition, packet_type)
            field_values = dict([(field, form[field]) for field in adapter.fields])
            adapter.packet_fields = field_values
            adapter.packet_type = packet_type
            adapter.packet_mapui = adapter.mapui
            return self.request.response.redirect(self.context.absolute_url())
        else:
            return self.template()

    def getAvailablePacketsInfo(self):
        return self.available_ptypes
