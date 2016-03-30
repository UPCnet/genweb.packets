from zope.component import getAdapter, getAdapters
from zope.annotation.interfaces import IAnnotations

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from genweb.core import utils
from genweb.packets.interfaces import IpacketDefinition
from genweb.packets import PACKETS_KEY
from genweb.packets import packetsMessageFactory as _

from pyquery import PyQuery as pq

from plone import api
import re
import requests
import urlparse


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

    def getTitle(self):
        return self.context.Title()

    def selectedPacket(self):
        if self.isAlreadyConfigured():
            annotations = IAnnotations(self.context)
            packet_key = annotations.get(PACKETS_KEY + '.type')
            packet_fields = annotations.get(PACKETS_KEY + '.fields')
            packet_mapui = annotations.get(PACKETS_KEY + '.mapui')
            selected = dict(packet_key=packet_key, value=packet_fields.get(packet_mapui.get('codi')), element=packet_fields.get(packet_mapui.get('element')))
        else:
            selected = {'packet_key': '', 'value': '', 'element': ''}

        return selected

    def isAlreadyConfigured(self):
        annotations = IAnnotations(self.context)
        if annotations.get(PACKETS_KEY + '.type', None):
            return True
        else:
            return False

    def getType(self):
        annotations = IAnnotations(self.context)
        return annotations.get(PACKETS_KEY + '.type', None)


class packetView(BrowserView):

    template = ViewPageTemplateFile('templates/view.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.title = ''
        self.content = ''

    def __call__(self):
        return self.template()

    def getHTML(self):
        packet_type = self.getType()
        adapter = getAdapter(self.context, IpacketDefinition, packet_type)
        adapter.packet_fields.update({'lang': utils.pref_lang()})

        url = adapter.URL_schema

        try:
            url = self.get_absolute_url(url % adapter.packet_fields)

            # check url to avoid autoreference, removing http(s) and final slash
            check_url = re.findall('https?(.*)\/?', url)[0].strip('/')
            check_parent = re.findall('https?(.*)\/?', self.context.absolute_url())[0].strip('/')

            # check url to avoid reference to root, removing language /xx
            check_root = re.findall('https?(.*)\/?', self.get_absolute_url(api.portal.get().absolute_url()))[0].strip('/')

            if check_url != check_parent and check_url.strip('/ca').strip('/es').strip('/en') != check_root:
                raw_html = requests.get(url)
                charset = re.findall('charset=(.*)"', raw_html.content)
                if len(charset) > 0:
                    clean_html = re.sub(r'[\n\r]?', r'', raw_html.content.decode(charset[0]))
                    doc = pq(clean_html)
                    match = re.search(r'This page does not exist', clean_html)
                    self.title = self.context.Title()  # titol per defecte
                    if not match:
                        if packet_type == 'contingut_genweb':
                            element = adapter.packet_fields['element']
                            if not element:
                                element = "#content-core"
                        else:
                            element = "#content-nucli"
                        content = pq('<div/>').append(
                            doc(self.data.element).outerHtml()).html(method='html')
                        if not content:
                            content = _(u"ERROR. This element does not exist.") + " " + self.data.element
                    else:
                        content = _(u"ERROR: Unknown identifier. This page does not exist." + url)
                else:
                    content = _(u"ERROR. Charset undefined")
            else:
                content = _(u"ERROR. Autoreference")
        except requests.exceptions.RequestException:
            content = _(u"ERROR. This URL does not exist.")
        except:
            content = _(u"ERROR. Unexpected exception.")

        self.content = content

    def getPacket(self):
        return self.content

    def getTitle(self):
        # import pdb; pdb.set_trace()
        # si el contingut esta configurat i encara no tenim el content, l'obtenim
        # el titol sera el nom del contingut (llistat, paquet o genweb) o el nom de l'estudi
        if self.isAlreadyConfigured() and self.content == '':
            self.getHTML()
        return self.title

    def getType(self):
        annotations = IAnnotations(self.context)
        return annotations.get(PACKETS_KEY + '.type', None)

    def isAlreadyConfigured(self):
        annotations = IAnnotations(self.context)
        if annotations.get(PACKETS_KEY + '.type', None):
            return True
        else:
            return False

    def selectedPacket(self):
        annotations = IAnnotations(self.context)
        packet_key = annotations.get(PACKETS_KEY + '.type')
        packet_fields = annotations.get(PACKETS_KEY + '.fields')
        packet_mapui = annotations.get(PACKETS_KEY + '.mapui')

        return dict(packet_key=packet_key, value=packet_fields.get(packet_mapui.get('codi')), element=packet_fields.get(packet_mapui.get('element')))

    def show_extended_info(self):
        user = api.user.get_current()

        if getattr(user, 'name', False):
            if user.name == 'Anonymous User':
                return False

        user_roles = set(api.user.get_roles(user=user, obj=self.context) +
                         api.user.get_roles(user=user))

        if 'Manager' in user_roles or \
           'WebMaster' in user_roles or \
           'Site Administrator' in user_roles or \
           'Owner' in user_roles:
            return True
        else:
            return False

    def get_absolute_url(self, url):
        """
        Convert relative url to absolute
        """
        if not ("://" in url):
            base = self.context.__parent__.absolute_url() + '/'
            return urlparse.urljoin(base, url)
        else:
            # Already absolute
            return url
