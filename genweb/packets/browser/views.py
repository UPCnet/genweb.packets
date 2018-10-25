from zope.site import hooks
from zope.component import getAdapter, getAdapters
from zope.annotation.interfaces import IAnnotations
from Products.PloneFormGen.interfaces import IPloneFormGenForm
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from genweb.core import utils
from genweb.packets.interfaces import IpacketDefinition
from genweb.packets import PACKETS_KEY
from genweb.packets import packetsMessageFactory as _

from pyquery import PyQuery as pq

import plone.api
import re
import requests
from requests.exceptions import RequestException, ReadTimeout


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

    def get_catalog_content(self, path_to_search):
        """ Fem una consulta al catalog, en comptes de fer un PyQuery """
        raw_html = u''
        catalog = getToolByName(self, 'portal_catalog')
        """ Mirem el cas especial dels form """
        im_searching_forms = catalog(path=path_to_search, object_provides=IPloneFormGenForm.__identifier__)
        if len(im_searching_forms) > 0:
            raw_html = im_searching_forms[0].getObject()()
        else:
            objects = catalog(path=path_to_search)
        try:
            raw_html = objects[0]()
        except:
            raw_html = objects[0].getObject()
        return raw_html

    def getHTML(self):
        packet_type = self.getType()
        adapter = getAdapter(self.context, IpacketDefinition, packet_type)
        adapter.packet_fields.update({'lang': utils.pref_lang()})

        try:
            if packet_type == 'contingut_genweb':
                packet = adapter.packet_fields
                urltype = packet['url_type']
                url = packet['url_contingut']
                element = packet['element']

                if urltype == 'internal':

                    link_intern = self.clean_url(url.lower())
                    root_url = self.clean_url(hooks.getSite().absolute_url())

                    if link_intern.startswith(root_url):
                        link_intern = link_intern.split('/', 1)[1]
                        raw_html = self.get_catalog_content(link_intern)()
                        charset = re.findall('charset=(.*)"', raw_html)
                        if len(charset) > 0:
                            clean_html = re.sub(r'[\n\r]?', r'', raw_html.encode(charset[0]))
                            doc = pq(clean_html)
                            if doc(element):
                                content = pq('<div/>').append(doc(element).outerHtml()).html(method='html')
                            else:
                                content = _(u"ERROR. This element does not exist:") + " " + element
                        else:
                            content = _(u"ERROR. Charset undefined")
                    else:
                        content = _(u"ERROR. This is not an inner content")

                elif urltype == 'external':

                    link_extern = self.clean_url(url.lower())
                    root_url = self.clean_url(hooks.getSite().absolute_url())

                    if link_extern.startswith(root_url):
                        content = _(u"ERROR. This is an inner content")
                    else:
                        raw_html = requests.get(url, timeout=5)
                        charset = re.findall('charset=(.*)"', raw_html.content)
                        if len(charset) > 0:
                            clean_html = re.sub(r'[\n\r]?', r'', raw_html.content.decode(charset[0]))
                            doc = pq(clean_html)
                            if doc(element):
                                content = pq('<div/>').append(doc(element).outerHtml()).html(method='html')
                            else:
                                content = _(u"ERROR. This element does not exist:") + " " + element
                        else:
                            content = _(u"ERROR. Charset undefined")
                else:
                    content = _(u"ERROR. Review the content configuration.")

        except ReadTimeout:
            content = _(u"ERROR. There was a timeout.")
        except RequestException:
            content = _(u"ERROR. This URL does not exist")
        except:
            content = _(u"ERROR. Unexpected exception")

        self.content = content

    def clean_url(self, url):
        """
        Clean http:// or https:// from a url
        """
        if url.startswith("http://"):
            url = url[7:]
        elif url.startswith("https://"):
            url = url[8:]

        return url

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
        user = plone.api.user.get_current()

        if getattr(user, 'name', False):
            if user.name == 'Anonymous User':
                return False
        try:
            user_roles = set(plone.api.user.get_roles(user=user, obj=self.context) +
                             plone.api.user.get_roles(user=user))
        except:
            user_roles = set(plone.api.user.get_roles(user=user, obj=self.context))

        if 'Manager' in user_roles or \
           'WebMaster' in user_roles or \
           'Site Administrator' in user_roles or \
           'Owner' in user_roles:
            return True
        else:
            return False
